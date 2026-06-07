const { request } = require('../../utils/request')

Page({
  data: {
    phases: [],
    stages: [],
    allStages: [],     // 保留完整数据用于筛选
    selectedPhase: 0,  // 0 = 全部
    selectedStage: null,
    showDetail: false,
    loading: true
  },

  onLoad() {
    this.loadProcess()
  },

  loadProcess() {
    this.setData({ loading: true })
    request({ url: '/api/process' })
      .then((res) => {
        if (res.code === 0) {
          const phases = res.data.phases || []
          const stages = res.data.stages || []
          this.setData({
            phases,
            stages,
            allStages: stages,
            loading: false
          })
        }
      })
      .catch(() => this.setData({ loading: false }))
  },

  // 切换工艺阶段筛选
  switchPhase(e) {
    const phaseId = e.currentTarget.dataset.phase
    const { allStages, selectedPhase } = this.data

    // 点击已选中的 tab 取消筛选
    const newPhase = selectedPhase === phaseId ? 0 : phaseId
    let filtered = allStages

    if (newPhase !== 0) {
      // 根据 phase id 找到对应的 phase name 来筛选 stages
      const phase = this.data.phases.find(p => p.id === newPhase)
      if (phase) {
        filtered = allStages.filter(s => s.phase === phase.name)
      }
    }

    this.setData({
      selectedPhase: newPhase,
      stages: filtered
    })
  },

  selectStage(e) {
    const stage = e.currentTarget.dataset.stage
    this.setData({ selectedStage: stage, showDetail: true })
  },

  closeDetail() {
    this.setData({ showDetail: false, selectedStage: null })
  },

  // 阻止事件冒泡（弹窗内部点击不关闭）
  noop() {}
})
