import psutil

from math import ceil
from charts import Chart, BarChart, Options
from colored import fg, attr, stylize
from tools import bytes_to_human_readable, ints_to_human_readable


class DiskUsage:
    """
    Personalize and visualize the disk space usage in the terminal

    options:
        barh: visualize values as a horizontal bar
        barv: visualiz disk space as a vertical bar
        pie: visualize as a pie charts
    """

    exclude = None
    details = True

    def __init__(
        self,
        path: str = "",
        exclude: list = None,
        details: bool = False,
        every: bool = False,
    ) -> None:
        self.path = path
        if exclude is None:
            self.exclude = []
        else:
            self.exclude = exclude
        self.details = details
        self.every = every

    def print_charts(self, options: Options = None) -> None:
        """Prints the charts based on user selection type"""
        if options is None:
            options = Options()

        parts = self.grab_partitions()

        ch = BarChart(options)
        for partname in parts:
            self.print_disk_chart(ch, partname, parts[partname])

    def print_disk_chart(self, chart: Chart, partname: str, part: dict) -> None:
        ch = chart
        title = (partname,)
        pre_graph_text = self.create_stats(part)
        if self.details:
            footer = self.create_details_text(part)
        else:
            footer = None

        maximum = part["total"]
        current = part["used"]
        post_graph_text = self.create_pct_used(part['percent'])

        ch.chart(
            post_graph_text=post_graph_text,
            title=title[0],
            pre_graph_text=pre_graph_text,
            footer=footer,
            maximum=maximum,
            current=current,
        )
        print()

    def switch(self) -> None:
        """
        Switch between printing all the
        partitions or only user specified.
        """
        if self.path:
            disks = self.grab_specific_disk(self.path[0])
        else:
            disks = self.grab_partitions(exclude=self.exclude, every=self.every)
        for disk in disks:
            self.print_horizontal_barchart(disk, disks[disk])

    def print_barchart(self, disk_name: str, disk: dict) -> None:
        """
        Prints disk usage in the Terminal with horizontal bars
        """
        print(f"{stylize(disk_name, self.header + self.style)}")
        print(self.create_stats(disk))
        chart = ChartPrint(self.graph, self.symbol)
        print(
            "",
            chart.draw_horizontal_bar(capacity=disk["total"],
                                used=disk["used"]),
                                self.create_warning(disk["percent"]),
        )
        if self.details:
            print(self.details_text(disk))
            print()

    def grab_partitions(self) -> dict:
        """Grabs all the partitions from the user's PC."""
        if self.exclude is None:
            exclude = []
        disks = {}
        # First append the root partition
        disks["root"] = {
            "total": psutil.disk_usage("/").total,
            "used": psutil.disk_usage("/").used,
            "free": psutil.disk_usage("/").free,
            "percent": psutil.disk_usage("/").percent,
            "fstype": psutil.disk_partitions(all=False)[0][2],
            "mountpoint": "/",
        }
        disk_parts = psutil.disk_partitions(all=self.every)
        for disk in disk_parts[1:]:
            # Exclude mounpoints created by snap
            if disk.device.startswith("/dev/loop"):
                continue
            # Check that part name is not in the excluded list
            if disk[1].split("/")[-1] in self.exclude:
                continue
            try:
                if psutil.disk_usage(disk[1]).total > 0:
                    disks[disk[1].split("/")[-1]] = {
                        "total": psutil.disk_usage(disk[1]).total,
                        "used": psutil.disk_usage(disk[1]).used,
                        "free": psutil.disk_usage(disk[1]).free,
                        "percent": psutil.disk_usage(disk[1]).percent,
                        "fstype": disk.fstype,
                        "mountpoint": disk.mountpoint,
                    }
            except:
                continue
        return disks

    def grab_specific_disk(self, path: str) -> dict:
        """
        Grabs data for the partition of the user specified path
        """
        disks = {}
        disks[path] = {
            "total": psutil.disk_usage(path).total,
            "used": psutil.disk_usage(path).used,
            "free": psutil.disk_usage(path).free,
            "percent": psutil.disk_usage(path).percent,
            "fstype": "N/A",
            "mountpoint": "N/A",
        }
        return disks

    def create_details_text(self, disk: dict) -> str:
        return f"fstype={disk['fstype']}\tmountpoint={disk['mountpoint']}"

    def create_stats(self, disk: dict) -> str:
        res = ints_to_human_readable(disk)
        return f"Total: {res['total']}\t Used: {res['used']}\t Free: {res['free']}"

    def create_pct_used(self, usage) -> str:
        """Create disk usage percent with warning color"""
        use = str(usage) + '% full'
        if usage >= 80:
            return f"{stylize(use, attr('blink') + fg(9))}"                  
        elif usage >= 60:
            return f"{stylize(use, fg(214))}"
        else:
            return f"{stylize(use, fg(82))}"

if __name__ == "__main__":
    self = DiskUsage()
    parts = self.grab_partitions()

    for partname in parts:
        part = parts[partname]
        ch = BarChart()
        title = (partname,)
        pre_graph_text = self.create_stats(part)
        footer = self.create_details_text(part)
        maximum = part["total"]
        current = part["used"]
        post_graph_text = self.create_pct_used(part['percent'])

        ch.chart(
            post_graph_text=post_graph_text,
            title=title[0],
            pre_graph_text=pre_graph_text,
            footer=footer,
            maximum=maximum,
            current=current,
        )
        print()
