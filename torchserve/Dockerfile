# 基于官方 TorchServe 镜像
FROM pytorch/torchserve:latest

WORKDIR /home/model-server

# 1. 拷贝模型仓库
COPY model_store/ ./model-store/

# 3. 拷贝配置和模型清单
COPY config.properties .
COPY models.yaml .

# 暴露接口端口
EXPOSE 8080 8081 8082

# 启动 TorchServe，并在前台打印日志
CMD ["torchserve", \
     "--start", \
     "--model-store", "model-store", \
     "--models", "vlm_model=vlm_model.mar", \
     "--ts-config", "config.properties", \
     "--foreground"]