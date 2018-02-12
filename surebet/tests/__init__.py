import json

from surebet.handling.surebets import *


class SurebetsJSONDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self._dict_to_surebets)

    def _dict_to_surebets(self, dict_json):
        if 'books_surebets' in dict_json:
            return self.parse_obj(dict_json, self.parse_surebets)
        elif {'book1', 'book2'}.issubset(dict_json):
            return self.parse_obj(dict_json, self.parse_book_surebets)
        elif {'teams1', 'teams2', 'parts'}.issubset(dict_json):
            return self.parse_obj(dict_json, self.parse_event_surebets)
        elif {'surebets', 'part'}.issubset(dict_json):
            return self.parse_obj(dict_json, self.parse_part_surebets)
        elif {'w1', 'w2', 'profit'}.issubset(dict_json):
            return self.parse_obj(dict_json, self.parse_surebet)
        elif {'name', 'factor'}.issubset(dict_json):
            return self.parse_obj(dict_json, self.parse_wager)
        else:
            raise json.JSONDecodeError('Unknown json structure')

    def parse_obj(self, dict_obj, parse_func):
        result = parse_func(dict_obj)
        self.parse_other_attrs(result, dict_obj)  # added this intermediate function for special cases that might be
        return result

    @staticmethod
    def parse_surebets(dict_surebets):
        result = Surebets()
        result.books_surebets = dict_surebets['books_surebets']
        return result

    @staticmethod
    def parse_book_surebets(dict_book_surebets):
        result = BookSurebets(dict_book_surebets['book1'], dict_book_surebets['book2'])
        del dict_book_surebets['book1']
        del dict_book_surebets['book2']

        for sport in dict_book_surebets:
            setattr(result, sport, dict_book_surebets[sport])
        return result

    @staticmethod
    def parse_event_surebets(dict_event_surebets):
        result = EventSurebets(dict_event_surebets['teams1'], dict_event_surebets['teams2'])
        for part_surebets in dict_event_surebets['parts']:
            result.parts.append(part_surebets)
        return result

    @staticmethod
    def parse_part_surebets(dict_part_surebets):
        return PartSurebets(dict_part_surebets['surebets'], dict_part_surebets['part'])

    @staticmethod
    def parse_surebet(dict_marked_surebet):
        if 'mark' in dict_marked_surebet:
            result = MarkedSurebet(dict_marked_surebet['w1'],
                                   dict_marked_surebet['w2'],
                                   dict_marked_surebet['profit'])
            result.mark = dict_marked_surebet['mark']
            if 'start_time' in dict_marked_surebet:
                result = TimedSurebet(result)
        else:
            result = Surebet(dict_marked_surebet['w1'],
                             dict_marked_surebet['w2'],
                             dict_marked_surebet['profit'])
        return result

    @staticmethod
    def parse_wager(wager_json):
        if 'cond' in wager_json:
            return CondWager(wager_json['name'], wager_json['factor'], wager_json['suffix'], wager_json['cond'])
        else:
            return Wager(wager_json['name'], wager_json['factor'])

    @staticmethod
    def parse_other_attrs(obj, dict_obj):
        for name_attr in dict_obj:
            if not hasattr(obj, name_attr):
                setattr(obj, name_attr, dict_obj[name_attr])
