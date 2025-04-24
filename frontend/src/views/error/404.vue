<template>
  <div class="error-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面不存在</h2>
      <p class="error-desc">抱歉，您访问的页面不存在或已被删除</p>
      <a-button type="primary" @click="$router.push('/')">
        <home-outlined /> 返回首页
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { HomeOutlined } from '@ant-design/icons-vue'
</script>

<style scoped>
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.error-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #1890ff;
  margin: 0;
}

.error-title {
  font-size: 24px;
  color: rgba(0, 0, 0, 0.85);
  margin: 16px 0;
}

.error-desc {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 24px;
}
</style>
