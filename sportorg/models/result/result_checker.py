from sportorg.core.otime import OTime
from sportorg.models.constant import StatusComments
from sportorg.models.memory import Person, ResultStatus, race, Result, ResultSportident


class ResultCheckerException(Exception):
    pass


class ResultChecker:
    def __init__(self, person: Person):
        assert person, Person
        self.person = person

    def check_result(self, result):
        if self.person is None:
            return True
        if self.person.group is None:
            return True

        if not result.is_sportident():
            return True

        course = race().find_course(self.person)

        return result.check(course)

    @classmethod
    def checking(cls, result):
        if result.person is None:
            raise ResultCheckerException('Not person')
        o = cls(result.person)
        if result.status == ResultStatus.OK or result.status == ResultStatus.DISQUALIFIED:
            result.status = ResultStatus.OK
            if not o.check_result(result):
                result.status = ResultStatus.DISQUALIFIED
                if not result.status_comment:
                    result.status_comment = StatusComments().get()

        return o

    @staticmethod
    def calculate_penalty(result):
        assert isinstance(result, Result)
        mode = race().get_setting('marked_route_mode', 'off')
        if mode == 'off':
            return

        person = result.person

        if person is None:
            return True
        if person.group is None:
            return True

        if not result.is_sportident():
            return True

        assert isinstance(result, ResultSportident)

        course = race().find_course(person)
        if not course:
            return True

        controls = course.controls

        penalty = ResultChecker.penalty_calculation(result.splits, controls, check_existence=True)

        if mode == 'laps':
            result.penalty_laps = penalty
        elif mode == 'time':
            time_for_one_penalty = OTime(msec=race().get_setting('marked_route_penalty_time', 60000))
            result.penalty_time = time_for_one_penalty * penalty

    @staticmethod
    def penalty_calculation(splits, controls, check_existence=False):
        user_array = [i.code for i in splits]
        origin_array = [i.get_int_code() for i in controls]
        return ResultChecker.penalty_calculation_int(user_array, origin_array, check_existence)

    @staticmethod
    def penalty_calculation_int(user_array, origin_array, check_existence=False):
        """:return quantity of incorrect or duplicated punches, order is ignored
            origin: 31,41,51; athlete: 31,41,51; result:0
            origin: 31,41,51; athlete: 31; result:0
            origin: 31,41,51; athlete: 41,31,51; result:0
            origin: 31,41,51; athlete: 31,42,51; result:1
            origin: 31,41,51; athlete: 31,41,51,52; result:1
            origin: 31,41,51; athlete: 31,42,51,52; result:2
            origin: 31,41,51; athlete: 31,31,41,51; result:1
            origin: 31,41,51; athlete: 31,41,51,51; result:1
            origin: 31,41,51; athlete: 32,42,52; result:3
            origin: 31,41,51; athlete: 31,41,51,61,71,81,91; result:4
            origin: 31,41,51; athlete: 31,41,52,61,71,81,91; result:5
            origin: 31,41,51; athlete: 51,61,71,81,91,31,41; result:4
            origin: 31,41,51; athlete: 51,61,71,81,91,32,41; result:5
            origin: 31,41,51; athlete: 51,61,71,81,91,32,42; result:6
            origin: 31,41,51; athlete: 52,61,71,81,91,32,42; result:7
            origin: 31,41,51; athlete: no punches; result:0

            with existence checking (if athlete has less punches, each missing add penalty):
            origin: 31,41,51; athlete: 31; result:2
            origin: 31,41,51; athlete: no punches; result:3
        """
        res = 0
        if check_existence and len(user_array) < len(origin_array):
            # add 1 penalty score for missing points
            res = len(origin_array) - len(user_array)

        for i in origin_array:
            # remove correct points (only one object per loop)
            if i in user_array:
                user_array.remove(i)

        # now user_array contains only incorrect and duplicated values
        res += len(user_array)

        return res
