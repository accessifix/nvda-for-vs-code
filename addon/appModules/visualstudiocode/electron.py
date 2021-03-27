from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible.chromium import Document

# Copied from the default NVDA add-on.
# @todo: Fix automatic switching to browse mode.
# It is useful when previewing Markdown documents as HTML.


class VSCodeDocument(Document):
	"""The only content in the root document node of Visual Studio code is the application object.
    Creating a tree interceptor on this object causes a major slow down of Code.
    Therefore, forcefully block tree interceptor creation.
    """

	_get_treeInterceptorClass = NVDAObject._get_treeInterceptorClass
