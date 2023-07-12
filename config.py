import argparse
from multiprocessing import cpu_count

class Config:
    def __init__(self):
        self.device = "cpu"
        self.is_half = False
        self.n_cpu = cpu_count()
        (self.python_cmd, self.colab, self.noparallel, self.noautoopen, self.api) = self.arg_parse()
        self.listen_port = 7860
        self.x_pad, self.x_query, self.x_center, self.x_max = self.device_config()

    @staticmethod
    def arg_parse() -> tuple:
        parser = argparse.ArgumentParser()
        parser.add_argument("--pycmd", type=str, default="python")
        parser.add_argument("--colab", action="store_true")
        parser.add_argument("--noparallel", action="store_true")
        parser.add_argument("--noautoopen", action="store_true")
        parser.add_argument("--api", action="store_true")
        cmd_opts = parser.parse_args()

        return (cmd_opts.pycmd, cmd_opts.colab, cmd_opts.noparallel, cmd_opts.noautoopen, cmd_opts.api)

    def device_config(self) -> tuple:
        x_pad = 1
        x_query = 6
        x_center = 38
        x_max = 41

        return x_pad, x_query, x_center, x_max