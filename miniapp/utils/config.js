// 开发时改为本机 IP，真机调试不能用 localhost
const BASE_URL = 'http://127.0.0.1:8000'

module.exports = {
  BASE_URL,
  API: {
    LOGIN: '/api/user/login',
    PROFILE: '/api/user/profile',
    RECOGNITION: '/api/recognition',
    CHAT: '/api/chat',
    KNOWLEDGE: '/api/knowledge',
    KNOWLEDGE_DETAIL: '/api/knowledge',
    KNOWLEDGE_SEARCH: '/api/knowledge/search/query',
    HISTORY: '/api/history',
    FAVORITE: '/api/favorite'
  }
}
