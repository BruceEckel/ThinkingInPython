# exercise_2.py
import warnings

@warnings.deprecated("Report is replaced by TextReport")
class Report:
    def render(self) -> str:
        return "report"

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    report = Report()  # type: ignore
    class Detailed(Report):  # type: ignore
        pass
print(report.render())
#: report
for entry in caught:
    print(entry.category.__name__, entry.message)
#: DeprecationWarning Report is replaced by TextReport
#: DeprecationWarning Report is replaced by TextReport
