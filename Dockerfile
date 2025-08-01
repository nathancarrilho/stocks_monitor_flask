# Dockerfile com imagem mais segura
FROM python:3.11-alpine

# Instala dependências do sistema necessárias
RUN apk add --no-cache gcc musl-dev

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Expõe a porta 5000 (onde o Flask roda)
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]