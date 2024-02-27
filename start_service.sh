echo "current llm: $llmname"

# echo "Starting fastchat controller..."
# nohup python3 -m fastchat.serve.controller --host 0.0.0.0 --port 30001 > /logs/fschat_controller.log 2>&1 &
# while [ `grep -E 'Uvicorn running on http://0.0.0.0:30001' /logs/fschat_controller.log | wc -l` -eq 0 ]; do
#     echo ">> Waiting for fastchat.serve.controller to start up"
#     sleep 3
# done

# echo "Starting fastchat model worker..."
# nohup python3 -m fastchat.serve.model_worker --model-name $llmname --model-path /llm --worker-address http://0.0.0.0:30002 --port 30002 --host 0.0.0.0 --controller-address http://0.0.0.0:30001 > /logs/fschat_model_worker.log 2>&1 &
# while [ `grep -E 'Uvicorn running on http://0.0.0.0:30002' /logs/fschat_model_worker.log | wc -l` -eq 0 ]; do
#     echo ">> Waiting for fastchat.serve.model_worker to start up"
#     sleep 3
# done

# echo "Starting fastchat openai api server..."
# nohup python3 -m fastchat.serve.openai_api_server --host 0.0.0.0 --port 30000 --controller-address http://0.0.0.0:30001 > /logs/fschat_api_server.log 2>&1 &
# while [ `grep -E 'Uvicorn running on http://0.0.0.0:30000' /logs/fschat_api_server.log | wc -l` -eq 0 ]; do
#     echo ">> Waiting for fastchat.serve.openai_api_server to start up"
#     sleep 3
# done

#echo "fastchat api service for [$llmname] started at <ip>:30000."

#echo "Installing requirements..."
#pip3 install -r /langchain-ChatGLM-dev/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

echo "Starting Chatchat Service..."
cd /ai/apps/Fenghou-Chat/
python3 /ai/apps/Fenghou-Chat/startup.py -a
#nohup python3 /langchain-chatchat/startup.py > /logs/chatchat.log 2>&1 &
#while [ `grep -E 'Application startup complete.' /logs/chatchat.log | wc -l` -eq 0 ]; do
#    echo ">> Waiting for Chatchat Service to start up."
#    sleep 3
#done

echo "All done."
