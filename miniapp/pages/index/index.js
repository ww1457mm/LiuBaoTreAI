Page({
  data: {
    banners: [
      { id: 1, title: '六堡茶 AI 识别', desc: '品种·等级·病害 一键识别', bg: 'linear-gradient(135deg,#3d7a35,#2d5a27)' },
      { id: 2, title: '智能问答', desc: 'RAG 知识库增强，答案可溯源', bg: 'linear-gradient(135deg,#5a8f4a,#3d6b32)' },
      { id: 3, title: '千年茶韵', desc: '探索茶船古道与非遗文化', bg: 'linear-gradient(135deg,#6b5344,#4a3728)' }
    ]
  },
  goIdentify() { wx.switchTab({ url: '/pages/identify/identify' }) },
  goChat() { wx.switchTab({ url: '/pages/chat/chat' }) },
  goKnowledge() { wx.navigateTo({ url: '/pages/knowledge/knowledge' }) },
  goHistory() { wx.navigateTo({ url: '/pages/history/history' }) }
})
