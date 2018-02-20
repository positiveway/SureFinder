from flask import Flask


def run_server(js_surebets):
    server = Flask(__name__)

    @server.route('/')
    def handle_index():
        return js_surebets.detailed_surebets

    server.run(host="0.0.0.0")
