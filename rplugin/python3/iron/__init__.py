# encoding:utf-8
""" iron.nvim (Interactive Repls Over Neovim).

`iron` is a plugin that allows better interactions with interactive repls
using neovim's job-control and terminal.
"""

import neovim


@neovim.plugin
class Iron(object):

    def __init__(self, nvim):
        self.__nvim = nvim
        self.__repls = {}
        self.__repl_templates = {
            'python': lambda: (
                nvim.eval("executable('ipython')") and "ipython" or "python"
            ),
            'clojure': lambda: (
                "lein repl"
            )
        }
        self.__current = -1

    def get_repl_template(self, ft):
        ft_repl = "iron_{}_repl".format(ft)

        if ft_repl in self.__nvim.vars:
            return self.__nvim.vars[ft_repl]
        else:
            return self.__repl_templates.get(ft, lambda: "")()


    @neovim.function("IronOpenRepl")
    def open_repl_for(self, args):
        self.__nvim.command('vnew')
        repl_id = self.__nvim.call('termopen', args[0])

        self.__repls[repl_id] = repl_id
        self.__current = repl_id

    @neovim.command("IronRepl")
    def get_repl(self):
        ft = self.__nvim.current.buffer.options["ft"]
        repl_type = self.get_repl_template(ft)

        if repl_type == "":
            self.__nvim.command("echoerr 'No repl found for {}'".format(ft))
        else:
            self.open_repl_for([repl_type])

    @neovim.function("IronSendToRepl")
    def send_to_repl(self, args):
        if args[0] == 'line':
            self.__nvim.command("""normal! '[V']"sy""")
        else:
            self.__nvim.command("""normal! `[v`]"sy""")

        data = self.__nvim.funcs.getreg('s')

        if any(map(lambda k: not k or k.isspace(), data.split('\n'))):
            data = "{}\n{}\n{}".format("%cpaste", data, "--")

        data += "\n"

        self.__nvim.call('jobsend', self.__current, data)
