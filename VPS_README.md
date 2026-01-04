# VPS部署快速参考

## 实际配置
- 项目路径: `/root/pdf-ck`
- 后端端口: 5000
- 前端端口: 8080
- Python: 3.10
- 关键依赖: pdf2docx==0.5.6

## 首次部署
```bash
scp deploy_vps.sh root@server:/root/
ssh root@server
chmod +x /root/deploy_vps.sh
bash /root/deploy_vps.sh
```

## 日常更新
```bash
# 本地推送
quick_push.bat "修改说明"

# VPS更新
ssh root@server "cd /root/pdf-ck && bash update_vps.sh"
```

## 常用命令
```bash
supervisorctl status                    # 查看状态
tail -f /var/log/pdf-tool-backend.log  # 查看日志
supervisorctl restart all               # 重启服务
```

完整文档见：vps_deployment_guide.md
