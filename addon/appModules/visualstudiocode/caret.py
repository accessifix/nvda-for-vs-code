	def event_caret(self):
		super(VSCodeEditor, self).event_caret()
		if self is api.getFocusObject() and not eventHandler.isPendingEvents('gainFocus'):
			self.detectPossibleSelectionChange()
		tx = self.makeTextInfo(textInfos.POSITION_SELECTION).copy()
		tx.collapse()
		tx.expand(textInfos.UNIT_LINE)
		lineStart = tx._start._startOffset
		if self.appModule.lastStartOffset == lineStart:
			return
		else:
			self.appModule.lastStartOffset = lineStart
			return
