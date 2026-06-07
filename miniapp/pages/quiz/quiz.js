const { request } = require('../../utils/request')

Page({
  data: {
    phase: 'start',
    questions: [],
    current: 0,
    selected: -1,
    answered: false,
    score: 0,
    results: [],
    grade: '',
    bestScore: 0,
    total: 10,
    // 预计算的选项状态
    optionStates: []
  },

  onLoad() {
    this.loadHistory()
  },

  loadHistory() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    if (!openid) return
    request({ url: '/api/quiz/history', data: { openid, page: 1, page_size: 1 } })
      .then((res) => {
        if (res.code === 0 && res.data && res.data.length > 0) {
          this.setData({ bestScore: res.data[0].score })
        }
      })
      .catch(() => {})
  },

  startQuiz() {
    request({ url: '/api/quiz/questions', data: { count: 10 } })
      .then((res) => {
        if (res.code === 0) {
          const questions = (res.data || []).map(q => ({
            id: q.id,
            q: q.q,
            options: q.options,
            explain: q.explain,
            selected: -1,
            correct: false
          }))
          // 预计算第一题的选项状态
          const firstQ = questions[0]
          const optionStates = firstQ ? firstQ.options.map((opt, i) => ({
            text: opt,
            isCorrect: false,
            isWrong: false,
            isSelected: false
          })) : []
          this.setData({
            phase: 'playing',
            questions,
            current: 0,
            selected: -1,
            answered: false,
            score: 0,
            results: [],
            optionStates
          })
        }
      })
      .catch(() => wx.showToast({ title: '加载题目失败', icon: 'none' }))
  },

  selectOption(e) {
    if (this.data.answered) return
    const idx = Number(e.currentTarget.dataset.idx)
    const { questions, current } = this.data
    const q = questions[current]
    const optionStates = q.options.map((opt, i) => ({
      text: opt,
      isCorrect: false,
      isWrong: false,
      isSelected: i === idx
    }))
    this.setData({ selected: idx, optionStates })
  },

  confirmAnswer() {
    if (this.data.answered || this.data.selected < 0) return
    const { questions, current, score } = this.data
    const q = questions[current]

    // 调后端判题（只传当前这一题）
    request({
      url: '/api/quiz/judge',
      method: 'POST',
      data: { answers: [{ id: q.id, answer: this.data.selected }] }
    }).then((res) => {
      if (res.code === 0) {
        const r = res.data.results[0]
        q.selected = this.data.selected
        q.correct = r.correct

        const optionStates = q.options.map((opt, i) => ({
          text: opt,
          isCorrect: i === r.correct_answer,
          isWrong: i === this.data.selected && i !== r.correct_answer,
          isSelected: false
        }))

        this.setData({
          questions,
          answered: true,
          score: r.correct ? score + 1 : score,
          optionStates
        })
      }
    }).catch(() => {
      // 网络错误时保守处理
      q.selected = this.data.selected
      q.correct = false
      this.setData({ questions, answered: true, optionStates: this.data.optionStates.map((s, i) => ({ ...s, isWrong: i === this.data.selected })) })
    })
  },

  nextQuestion() {
    const { current, questions } = this.data
    if (current < questions.length - 1) {
      const nextIdx = current + 1
      const nextQ = questions[nextIdx]
      const optionStates = nextQ ? nextQ.options.map((opt) => ({
        text: opt,
        isCorrect: false,
        isWrong: false,
        isSelected: false
      })) : []
      this.setData({
        current: nextIdx,
        selected: -1,
        answered: false,
        optionStates
      })
    } else {
      this.submitResult()
    }
  },

  submitResult() {
    const openid = getApp().globalData.openid || wx.getStorageSync('openid')
    const { questions, score } = this.data
    const answers = questions.map(q => ({ id: q.id, answer: q.selected }))

    request({ url: '/api/quiz/submit', method: 'POST', data: { openid, answers } })
      .then((res) => {
        if (res.code === 0) {
          this.setData({
            phase: 'result',
            results: res.data.results || [],
            grade: res.data.grade || '',
            score: res.data.score || score
          })
          this.loadHistory()
        }
      })
      .catch(() => {
        this.setData({ phase: 'result' })
      })
  },

  restart() {
    this.setData({ phase: 'start' })
  },

  noop() {}
})
