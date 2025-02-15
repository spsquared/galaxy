import type React from "react";
import { useMemo, useState } from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import NoDataToDisplay from "highcharts/modules/no-data-to-display";
import {
  type ChartData,
  type PlotLine,
  highchartsOptionsBase,
} from "./chartUtils";

NoDataToDisplay(Highcharts);

export interface ChartBaseProps {
  yAxisLabel: string;
  values?: Record<string, ChartData[]>;
  loading?: boolean;
  loadingMessage?: string;
  plotLines?: PlotLine[];
  crownTop?: boolean;
  xAxisEndDate?: Date;
}

const ChartBase: React.FC<ChartBaseProps> = ({
  yAxisLabel,
  values,
  loading = false,
  loadingMessage,
  plotLines,
  crownTop = false,
  xAxisEndDate = new Date(),
}) => {
  // Translate values into Highcharts compatible options
  const [myChart, setChart] = useState<Highcharts.Chart>();

  const seriesData: Highcharts.SeriesOptionsType[] = useMemo(() => {
    if (values === undefined) return [];
    return Object.keys(values).map((key) => ({
      type: "line",
      name: key,
      data: values[key],
      marker: {
        enabled: false,
        symbol: "circle",
      },
    }));
  }, [values]);

  if (myChart !== undefined) {
    try {
      if (loading) myChart.showLoading(loadingMessage ?? "Loading...");
      else myChart.hideLoading();
    } catch (_) {
      // Ignore internal highcharts errors...
    }
  }

  const options: Highcharts.Options = {
    ...highchartsOptionsBase,
    lang: {
      loading: loadingMessage ?? "Loading...",
      noData: "No data found to display.",
    },
    noData: {
      style: {
        fontWeight: "bold",
        fontSize: "15px",
        color: "red",
      },
    },
    loading: {
      style: {
        fontWeight: "bold",
        fontSize: "18px",
        color: "teal",
      },
    },
    chart: {
      ...highchartsOptionsBase.chart,
      height: 400,
    },
    yAxis: {
      title: {
        text: yAxisLabel,
      },
    },
    title: {
      text: "",
    },
    credits: {
      href: "https://jmerle.github.io/battlecode-2024-statistics/",
      text: "Inspired by jmerle",
    },
    tooltip: {
      ...highchartsOptionsBase.tooltip,
      formatter: function () {
        // Add crown emoji on the top player at the time

        // Very first element is the header at the bottom
        const x: string | undefined = this.x?.toString();
        let header = "ERROR";
        if (x !== undefined)
          header = Highcharts.dateFormat("%A, %e %b, %l:%M %p", Number(x));

        const names = [header];

        let max = -1;
        let index = -1;
        this.points?.forEach((point, i) => {
          const y = point.y ?? -1;
          let color: string | undefined = point.color?.toString();
          if (color === undefined) color = "red";
          const circle = `<span class="circle" style="color: ${color};">●</span>`;
          if (y > max) {
            max = y;
            index = i;
          }
          names.push(
            circle + " " + point.series.name + ": <b>" + y.toString() + "</b>",
          );
        });

        if (index !== -1 && crownTop)
          names[index + 1] = "👑 " + names[index + 1];

        return names;
      },
    },
    series: seriesData,

    legend: {
      layout: "horizontal",
      align: "center",
      verticalAlign: "bottom",
      // width: 100,
      maxHeight: 1e6,
      alignColumns: false,
    },

    xAxis: {
      ...highchartsOptionsBase.xAxis,
      type: "datetime",
      title: {
        text: "Local Date & Time",
      },
      crosshair: {
        width: 1,
      },
      dateTimeLabelFormats: {
        day: "%e %b",
        hour: "%I:%M %P",
        minute: "%I:%M:%S %P",
      },
      plotLines: plotLines?.map(([name, timestamp]) => ({
        color: "#ccd6eb",
        zIndex: 1000,
        value: timestamp,
        label: {
          text: name,
          useHTML: true,
          x: 12,
          y: 0,
          rotation: 270,
          align: "left",
          verticalAlign: "bottom",
          style: {
            background: "rgba(255, 255, 255, 0.5)",
            color: "#000000",
            padding: "3px",
            border: "1px solid #ccd6eb",
            borderTop: "0",
          },
        },
      })),
      max: Math.min(xAxisEndDate.getTime(), Date.now()),
    },
  };

  return (
    <div>
      <HighchartsReact
        classname="w-full"
        highcharts={Highcharts}
        options={options}
        callback={(chart: Highcharts.Chart) => {
          setChart(chart);
        }}
      />
    </div>
  );
};

export default ChartBase;
