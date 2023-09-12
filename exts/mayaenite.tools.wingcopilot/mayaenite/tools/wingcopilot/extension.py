
import carb
import omni.ext             
import asyncio
import socket

#-------------------------------------------------------------------------------
def _get_event_loop() -> asyncio.AbstractEventLoop:
	"""getting the event loop"""
	try:
		return asyncio.get_running_loop()
	except RuntimeError:
		return asyncio.get_event_loop_policy().get_event_loop()

class MayaeniteToolsWingcopilotExtension(omni.ext.IExt):
	# ext_id is current extension id. It can be used with extension manager to query additional information, like where
	# this extension is located on filesystem.
	def on_startup(self, ext_id):
		print("[mayaenite.tools.wingcopilot] mayaenite tools wingcopilot startup")
		#self._globals = {**globals()}
		#self._locals = self._globals
		################################################################################
		class ServerProtocol(asyncio.Protocol):
			#---------------------------------------------------------------------------
			def __init__(self, parent) -> None:
				super().__init__()
				self._parent = parent
			#---------------------------------------------------------------------------
			def connection_made(self, transport):
				transport.get_extra_info('peername')
				self.transport = transport
			#---------------------------------------------------------------------------
			def data_received(self, data):
				#asyncio.run_coroutine_threadsafe(self._parent._exec_code_async(data.decode(), self.transport),_get_event_loop())
				try:
					code = compile(data.decode(), "<string>", "exec", dont_inherit=True)
					eval(code, {**globals()}, {**globals()})
				except Exception as e:
					carb.log_error(str(e))

		async def server_task():
			try:
				self._server = await _get_event_loop().create_server(protocol_factory=lambda: ServerProtocol(self),host="127.0.0.1",port=6000,family=socket.AF_INET)
			except Exception as e:
				self._server = None
				self._socket_last_error = str(e)
				carb.log_error(str(e))
				return
			await self._server.start_serving()

		self._task = _get_event_loop().create_task(server_task())
		
	def on_shutdown(self):
		print("[mayaenite.tools.wingcopilot] mayaenite tools wingcopilot shutdown")
		if self._server:
			self._server.close()
			_get_event_loop().run_until_complete(self._server.wait_closed())
			self._server = None
		self._task = None