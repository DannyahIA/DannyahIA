import datetime
import re

README_PATH = "README.md"
START_DATE = datetime.date(2023, 7, 1)

# Calculate experience time
today = datetime.date.today()
delta = today - START_DATE
years = delta.days // 365
months = (delta.days % 365) // 30
experience = f"{years} years and {months} months"

svg_link = f"[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&duration=4000&repeat=false&pause=750&color=EB6F92&center=true&vCenter=true&random=true&width=800&lines=Experience:+{years}+years+and+{months}+months)](https://git.io/typing-svg)"

# Update the README
with open(README_PATH, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"(<!-- EXPERIENCE_START -->)(.*?)(<!-- EXPERIENCE_END -->)"
new_content = re.sub(pattern, rf"\1\n{svg_link}\n\3", content, flags=re.DOTALL)

with open(README_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"README.md updated with experience time: {experience}")
