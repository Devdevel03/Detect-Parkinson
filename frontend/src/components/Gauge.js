import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function Gauge({ probability }) {
  const ref = useRef();
  const width = 250;
  const height = 150;

  useEffect(() => {
    // Clear previous SVG
    d3.select(ref.current).selectAll("*").remove();
    
    const svg = d3.select(ref.current)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height * 0.8})`);

    const angle = d3.scaleLinear()
      .domain([0, 1])
      .range([-Math.PI / 2, Math.PI / 2]);

    const radius = 80;

    // The background arc
    const backgroundArc = d3.arc()
      .innerRadius(radius - 20)
      .outerRadius(radius)
      .startAngle(-Math.PI / 2)
      .endAngle(Math.PI / 2);

    svg.append("path")
      .attr("d", backgroundArc)
      .attr("fill", "#ecf0f1");

    // The foreground arc (the value)
    const foregroundArc = d3.arc()
      .innerRadius(radius - 20)
      .outerRadius(radius)
      .startAngle(-Math.PI / 2)
      .endAngle(angle(probability));

    svg.append("path")
      .attr("d", foregroundArc)
      .attr("fill", d3.interpolateRgb("green", "red")(probability));

    // The label
    svg.append("text")
      .attr("text-anchor", "middle")
      .attr("font-size", "24px")
      .attr("font-weight", "bold")
      .attr("dy", "0.3em")
      .text(`${(probability * 100).toFixed(1)}%`);
      
    // Sub-labels
    svg.append("text")
      .attr("text-anchor", "start")
      .attr("font-size", "12px")
      .attr("fill", "green")
      .attr("transform", `translate(${-radius-5}, 15)`)
      .text("Healthy");

    svg.append("text")
      .attr("text-anchor", "end")
      .attr("font-size", "12px")
      .attr("fill", "red")
      .attr("transform", `translate(${radius+5}, 15)`)
      .text("Parkinson's");

  }, [probability]);

  return <svg ref={ref}></svg>;
}

export default Gauge;