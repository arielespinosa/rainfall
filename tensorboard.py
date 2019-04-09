#from tensorboard import default
from tensorboard import program

tb = program.TensorBoard(default.PLUGIN_LOADERS, default.get_assets_zip_provider())
tb.configure(argv=['--logdir', my_directory])
tb.main()


class TensorBoardTool:

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def run(self):
        # Remove http messages
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        # Start tensorboard server
        tb = program.TensorBoard(default.PLUGIN_LOADERS, default.get_assets_zip_provider())
        tb.configure(argv=['--logdir', self.dir_path])
        url = tb.launch()
        sys.stdout.write('TensorBoard at %s \n' % url)

tb_tool = TensorBoardTool('tensorboard')
tb_tool.run()