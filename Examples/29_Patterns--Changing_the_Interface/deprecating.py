# deprecating.py
import warnings

class Report:
    def render(self) -> str:
        return "report"

    @warnings.deprecated(
        "Report.to_string() is replaced by render()")
    def to_string(self) -> str:
        return self.render()

report = Report()
print(report.render())
#: report
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    print(report.to_string())  # type: ignore
#: report
print(caught[0].category.__name__)
#: DeprecationWarning
print(caught[0].message)
#: Report.to_string() is replaced by render()
