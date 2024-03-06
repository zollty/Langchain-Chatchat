from fastapi import Body, File, Form, UploadFile
from server.utils import (wrap_done, BaseResponse, get_temp_dir, run_in_thread_pool)
from typing import AsyncIterable, List, Optional
import asyncio
from server.knowledge_base.utils import KnowledgeFile
import json
import os
from pathlib import Path


def _parse_files_in_thread(
    files: List[UploadFile],
    dir: str
):
    """
    通过多线程将上传的文件保存到对应目录内。
    生成器返回保存结果：[success or error, filename, msg, docs]
    """
    def parse_file(file: UploadFile) -> dict:
        '''
        保存单个文件。
        '''
        try:
            filename = file.filename
            file_path = os.path.join(dir, filename)
            file_content = file.file.read()  # 读取上传文件的内容

            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, "wb") as f:
                f.write(file_content)
            kb_file = KnowledgeFile(filename=filename, knowledge_base_name="temp")
            kb_file.filepath = file_path
            docs = kb_file.file2docs()
            return True, filename, f"成功上传文件 {filename}", docs
        except Exception as e:
            msg = f"{filename} 文件上传失败，报错信息为: {e}"
            return False, filename, msg, []

    params = [{"file": file} for file in files]
    for result in run_in_thread_pool(parse_file, params=params):
        yield result


def parse_docs(
    files: List[UploadFile] = File(..., description="上传文件，支持多文件")
) -> BaseResponse:
    failed_files = []
    documents = []
    path, id = get_temp_dir()
    print("--------------------------update file, save dir: ")
    print(id)
    rt_success = False
    for success, file, msg, docs in _parse_files_in_thread(files=files, dir=path):
        if success:
            documents += docs
            print(f"{file}--------------------------update file success: ")
            # print(docs)
            rt_success = True
        else:
            failed_files.append({file: msg})
            print(f"{file}--------------------------update file failed: ")
            print(msg)
    if rt_success:
        return BaseResponse(code=200, msg="文件上传与解析完成", data={"id":id, "docs": documents, "failed_files": failed_files})
    return BaseResponse(code=500, msg="解析文件失败", data={"failed_files": failed_files})
