from __future__ import print_function
import sys
import multiprocessing
import subprocess
import gtp
from AlphaGo import go
from AlphaGo.util import save_gamestate_to_sgf

GNUGO_TAKEOVER = 220

def run_gnugo(sgf_file_name, command):
    from distutils import spawn
    if spawn.find_executable('gnugo'):
        from subprocess import Popen, PIPE
        p = Popen(['gnugo', '--chinese-rules', '--mode', 'gtp', '-l', sgf_file_name],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out_bytes = p.communicate(input=command)[0]
        return out_bytes.decode('utf-8')[2:]
    else:
        return ''


class ExtendedGtpEngine(gtp.Engine):

    recommended_handicaps = {
        2: "D4 Q16",
        3: "D4 Q16 D16",
        4: "D4 Q16 D16 Q4",
        5: "D4 Q16 D16 Q4 K10",
        6: "D4 Q16 D16 Q4 D10 Q10",
        7: "D4 Q16 D16 Q4 D10 Q10 K10",
        8: "D4 Q16 D16 Q4 D10 Q10 K4 K16",
        9: "D4 Q16 D16 Q4 D10 Q10 K4 K16 K10"
    }

    '''
    def call_gnugo(self, sgf_file_name, command):
        try:
            pool = multiprocessing.Pool(processes=1)
            result = pool.apply_async(run_gnugo, (sgf_file_name, command))
            output = result.get(timeout=10)
            pool.close()
            return output
        except multiprocessing.TimeoutError:
            pool.terminate()
            # if can't get answer from GnuGo, return no result
            return ''
    '''

    def cmd_time_left(self, arguments):
        pass

    def cmd_place_free_handicap(self, arguments):
        try:
            number_of_stones = int(arguments)
        except Exception:
            raise ValueError('Number of handicaps could not be parsed: {}'.format(arguments))
        if number_of_stones < 2 or number_of_stones > 9:
            raise ValueError('Invalid number of handicap stones: {}'.format(number_of_stones))
        vertex_string = ExtendedGtpEngine.recommended_handicaps[number_of_stones]
        self.cmd_set_free_handicap(vertex_string)
        return vertex_string

    def cmd_set_free_handicap(self, arguments):
        vertices = arguments.strip().split()
        moves = [gtp.parse_vertex(vertex) for vertex in vertices]
        self._game.place_handicaps(moves, arguments)

    def cmd_final_score(self, arguments):
        return self._game.proxy_final_score(arguments)
        # sgf_file_name = self._game.get_current_state_as_sgf()
        # return self.call_gnugo(sgf_file_name, 'final_score\n')

    def cmd_final_status_list(self, arguments):
        return self._game.proxy_final_status_list(arguments)
        # sgf_file_name = self._game.get_current_state_as_sgf()
        # return self.call_gnugo(sgf_file_name, 'final_status_list {}\n'.format(arguments))

    def cmd_genmove(self, arguments):
        response = self._game.proxy_genmove(arguments)
        if response is None:
            return super(ExtendedGtpEngine, self).cmd_genmove(arguments)
        return response

    def cmd_play(self, arguments):
        response = self._game.proxy_play(arguments)
        if response is None:
            return super(ExtendedGtpEngine, self).cmd_play(arguments)
        return response

    def cmd_load_sgf(self, arguments):
        pass

    def cmd_save_sgf(self, arguments):
        pass

    # def cmd_kgs_genmove_cleanup(self, arguments):
    #     return self.cmd_genmove(arguments)


color_names = { gtp.EMPTY:"e", gtp.BLACK:"b", gtp.WHITE:"w", }

def coords_from_str(s):
    x = ord(s[0].upper()) - ord('A')
    if x >= 9: x -= 1
    y = int(s[1:])
    y -= 1
    return x,y

def str_from_coords(x, y):
    if x >= 8: x += 1
    return chr(ord('A')+x) + str(y+1)

class GTPGameConnector(object):
    """A class implementing the functions of a 'game' object required by the GTP
    Engine by wrapping a GameState and Player instance
    """
    
    def __init__(self, player, helper_level=3, debug=False):
        self._state = go.GameState(enforce_superko=True)
        self._player = player
        self._helper_level = helper_level   
        self._debug = debug
        if helper_level > 0:
            command = ["gnugo", "--mode", "gtp", "--level", str(helper_level), "--chinese-rules", "--positional-superko"]
            self._proc = subprocess.Popen(command, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE) # bufsize=1 is line buffered

    def print_debug(self, msg):
        if self._debug:
            with open("gtp_debug.log", "a") as f:
                f.write(msg + "\n")

    def gnugo_command(self, command):
        if self._helper_level > 0:
            self.print_debug("HelperEngine: sending command \"{}\"".format(command))
            self._proc.stdin.write(command)
            self._proc.stdin.write('\n')
        
            response = ""
            while True:
                line = self._proc.stdout.readline()
                if line.startswith('='):
                    response += line[2:]
                elif line.startswith('?'):
                    self.print_debug("HelperEngine: error response! line is \"{}\"".format(line))
                    response += line[2:]
                elif len(line.strip()) == 0:
                    # blank line ends response
                    break
                else:
                    response += line
            response = response.strip()
            self.print_debug("HelperEngine: got response \"{}\"".format(response))
            return response
        return ""

    def call_gnugo(self, command):
        self._proc.stdin.write(command)
        self._proc.stdin.write('\n')
        self.print_debug("HelperEngine2: sending command \"{}\"".format(command))
    
        response = ""
        while True:
            line = self._proc.stdout.readline()
            if len(line.strip()) == 0:
                # blank line ends response
                break
            else:
                response += line
        response = response.strip()
        self.print_debug("HelperEngine2: response \"{}\"".format(response))
        return response

    def clear(self):
        self._state = go.GameState(self._state.size, enforce_superko=True)
        self.gnugo_command("clear_board")

    def make_move(self, color, vertex):
        # vertex in GTP language is 1-indexed, whereas GameState's are zero-indexed
        try:
            if vertex == gtp.PASS:
                self._state.do_move(go.PASS_MOVE)
                self.gnugo_command("play {} pass".format(color_names[color]))
            elif vertex == gtp.RESIGN:
                pass
            else:
                (x, y) = vertex
                self._state.do_move((x - 1, y - 1), color)
                self.gnugo_command("play {} {}".format(color_names[color], str_from_coords(x-1, y-1)))
            return True
        except go.IllegalMove:
            return False

    def set_size(self, n):
        self._state = go.GameState(n, enforce_superko=True)
        self.gnugo_command("boardsize {}".format(n))

    def set_komi(self, k):
        self._state.komi = k
        self.gnugo_command("komi {:.2f}".format(k))

    def get_move(self, color):
        self._state.current_player = color
        move = self._player.get_move(self._state)
        if move == go.PASS_MOVE:
            return gtp.PASS
        else:
            (x, y) = move
            return (x + 1, y + 1)

    def get_current_state_as_sgf(self):
        from tempfile import NamedTemporaryFile
        temp_file = NamedTemporaryFile(delete=False)
        save_gamestate_to_sgf(self._state, '', temp_file.name)
        return temp_file.name

    def place_handicaps(self, vertices, arguments):
        actions = []
        for vertex in vertices:
            (x, y) = vertex
            actions.append((x - 1, y - 1))
            # gnu command
        self._state.place_handicaps(actions)
        self.call_gnugo("set_free_handicap {}".format(arguments))

    def proxy_final_score(self, arguments):
        return self.call_gnugo('final_score')[2:]

    def proxy_final_status_list(self, arguments):
        return self.call_gnugo('final_status_list {}'.format(arguments))[2:]

    def proxy_genmove(self, arguments):
        n = len(self._state.history)
        if n >= GNUGO_TAKEOVER:
            return self.call_gnugo("genmove {}".format(arguments))[2:]
        else:
            return None

    def proxy_play(self, arguments):
        n = len(self._state.history)
        if n >= GNUGO_TAKEOVER:
            return self.call_gnugo("play {}".format(arguments))[2:]
        else:
            return None


def run_gtp(player_obj, inpt_fn=None, name="Gtp Player", version="0.0", helper_level=10, debug=False):
    gtp_game = GTPGameConnector(player_obj, helper_level=helper_level, debug=debug)
    gtp_engine = ExtendedGtpEngine(gtp_game, name, version)
    if inpt_fn is None:
        inpt_fn = raw_input

    sys.stderr.write("GTP engine ready\n")
    sys.stderr.flush()
    while not gtp_engine.disconnect:
        inpt = inpt_fn()
        # handle either single lines at a time
        # or multiple commands separated by '\n'
        try:
            cmd_list = inpt.split("\n")
        except:
            cmd_list = [inpt]
        for cmd in cmd_list:
            engine_reply = gtp_engine.send(cmd)
            sys.stdout.write(engine_reply)
            sys.stdout.flush()
