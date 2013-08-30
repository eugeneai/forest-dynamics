package org.icc.fd;


/* --------------------
 * AnnotationDemo1.java
 * --------------------
 * (C) Copyright 2002-2006, by Object Refinery Limited.
 *
 */

// package demo;

import java.awt.Font;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;

import javax.swing.JPanel;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.annotations.XYTextAnnotation;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.title.TextTitle;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;
import org.jfree.ui.TextAnchor;

/**
 * A demo showing chart annotations.
 */
public class SimpleFDSimulationPresenter extends ApplicationFrame {

    /**
     * Creates a new demo application.
     *
     * @param title  the frame title.
     */
    public SimpleFDSimulationPresenter(String title, FDModel model) {

        super(title);
        XYSeriesCollection dataset = createDataset(model);
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(900, 700));
        setContentPane(chartPanel);

    }

    /**
     * Creates a dataset.
     *
     * @return a dataset.
     */
    private static XYSeriesCollection createDataset(FDModel model) {

        XYSeriesCollection result = new XYSeriesCollection();

        for (String k: model.symbolTable.keySet()) {
            XYSeries s = model.getSeries(k);
            result.addSeries(s);
        }
        return result;

    }

    /**
     * Creates a sample chart.
     *
     * @param dataset  the dataset.
     *
     * @return A sample chart.
     */
    private static JFreeChart createChart(XYDataset dataset) {
        JFreeChart chart = ChartFactory.createXYLineChart(
                "Forest Dynamics Simulated Time Series",
                "Year",
                "Area / Rate",
                dataset,
                PlotOrientation.VERTICAL,
                true,
                true,
                false
        );
        /*
        TextTitle t1 = new TextTitle("Growth Charts: United States",
                new Font("SansSerif", Font.BOLD, 14));
        TextTitle t2 = new TextTitle(
                "Weight-for-age percentiles: boys, birth to 36 months",
                new Font("SansSerif", Font.PLAIN, 11));
        chart.addSubtitle(t1);
        chart.addSubtitle(t2);
        */
        XYPlot plot = chart.getXYPlot();
        NumberAxis domainAxis = (NumberAxis) plot.getDomainAxis();
        domainAxis.setUpperMargin(0.12);
        domainAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());
        NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setAutoRangeIncludesZero(false);

        /*
        // add some annotations...
        XYTextAnnotation annotation = null;
        Font font = new Font("SansSerif", Font.PLAIN, 9);

        annotation = new XYTextAnnotation("3rd", 36.5, 11.76);
        annotation.setFont(font);
        annotation.setTextAnchor(TextAnchor.HALF_ASCENT_LEFT);
        plot.addAnnotation(annotation);

        annotation = new XYTextAnnotation("5th", 36.5, 12.04);
        annotation.setFont(font);
        annotation.setTextAnchor(TextAnchor.HALF_ASCENT_LEFT);
        plot.addAnnotation(annotation);
        */

        return chart;
    }

    /**
     * Starting point for the demonstration application when it is run as
     * a stand-alone application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {
        FDModel model = FDModelTest.test_one();
        SimpleFDSimulationPresenter application = new SimpleFDSimulationPresenter("Forest Dynamics Time Series", model);
        application.pack();
        RefineryUtilities.centerFrameOnScreen(application);
        application.setVisible(true);
    }

}