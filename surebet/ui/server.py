from flask import Flask

from surebet.ui import *

templates_dir = os.path.join(package_dir, "templates")
static_dir = os.path.join(package_dir, "static")


def run_server(safe_surebets):
    server = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

    @server.route('/')
    def handle_index():
        table_lines = render_table_lines()
        with open(os.path.join(templates_dir, "index.html")) as out:
            index_str = out.read()

        return index_str.replace("TABLE_LINES", table_lines)

    def render_table_lines():
        with open(os.path.join(templates_dir, "table_line.html")) as out:
            line_template = out.read()

        table_lines = []
        for surebet in safe_surebets.detailed_surebets:
            format_args = {
                "book1": surebet.book1,
                "book2": surebet.book2,
                "sport": get_sport_name(surebet.sport),
                "teams1": surebet.teams1,
                "teams2": surebet.teams2,
                "part": "part: {}".format(surebet.part),
                "w1_name": repr(surebet.w1),
                "w2_name": repr(surebet.w2),
                "w1_factor": surebet.w1.factor,
                "w2_factor": surebet.w2.factor,
                "lifetime": surebet.lifetime,
                "profit": surebet.profit,
                "league": "",
                "time": "",
                "score": "",
            }

            table_lines.append(line_template.format(**format_args))

        return "\n".join(table_lines)

    def get_sport_name(sport):
        return {
            "soccer": "soccer",
            "hockey": "hockey",
            "basket": "basketball",
            "tennis": "tennis",
            "volley": "volleyball",
        }[sport]

    server.run(host="0.0.0.0")
