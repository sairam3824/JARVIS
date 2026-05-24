FROM node:22-alpine

WORKDIR /workspace/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY . /workspace

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

