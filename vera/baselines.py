class BaselineEvaluator:
    @staticmethod
    def visible_tests_only(result):
        return (
            result.tests_failed == 0
            and result.tests_passed > 0
        )

    @staticmethod
    def visible_and_hidden_tests(result):
        return (
            result.tests_failed == 0
            and result.hidden_tests_failed == 0
            and result.tests_passed > 0
            and result.hidden_tests_passed > 0
        )

    @staticmethod
    def vera_decision(result):
        return result.accepted