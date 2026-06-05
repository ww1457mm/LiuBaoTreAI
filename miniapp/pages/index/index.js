Page({
  data: {
    banners: [
      { id: 1, tag: 'AI 识别', title: '六堡茶 AI 识别', desc: '品种·等级·病害 一键智能识别', bg: 'linear-gradient(135deg, #3d7a35 0%, #2d5a27 60%, #1e3d1a 100%)' },
      { id: 2, tag: '智能问答', title: '茶文化百科助手', desc: 'RAG 知识库增强，答案可溯源', bg: 'linear-gradient(135deg, #5a8f4a 0%, #3d6b32 60%, #2d5a27 100%)' },
      { id: 3, tag: '千年茶韵', title: '探索茶船古道', desc: '非遗文化与六堡茶历史传承', bg: 'linear-gradient(135deg, #8b7355 0%, #6b5344 60%, #4a3728 100%)' }
    ]
  },
  goIdentify() { wx.switchTab({ url: '/pages/identify/identify' }) },
  goChat() { wx.switchTab({ url: '/pages/chat/chat' }) },
  goKnowledge() { wx.navigateTo({ url: '/pages/knowledge/knowledge' }) },
  goHistory() { wx.navigateTo({ url: '/pages/history/history' }) }
})
