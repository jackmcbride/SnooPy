from snoopy import df
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool, ColumnDataSource
from datetime import date

df["Start_string"]=df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["End_string"]=df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")

cds=ColumnDataSource(df)

d=date.today()

p=figure(x_axis_type="datetime", height=100, width=500, responsive=True, title="Activity on: " + d.strftime('%Y_%m_%d'))
p.title.align = "center"
p.title.text_font_size="22pt"
p.title.text_color="grey"
p.title.text_font_style = "bold"
p.yaxis.minor_tick_line_color = None
p.ygrid[0].ticker.desired_num_ticks=1

p.quad(left = "Start", right = "End", top=1, bottom=0, color="green", source=cds)

hover=HoverTool(tooltips=[("Start", "@Start_string"), ("End", "@End_string")])
p.add_tools(hover)

output_file(d.strftime('%Y_%m_%d') + ".html")

show(p)