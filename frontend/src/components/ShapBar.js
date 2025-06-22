import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function ShapBar({ shapValues }) {
  const ref = useRef();

  useEffect(() => {
    if (!shapValues || shapValues.length === 0) return;

    // Sort values by their absolute impact and take top 10
    const sortedValues = [...shapValues]
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
      .slice(0, 10)
      .reverse(); // Reverse for vertical bar chart display

    // Clear previous SVG
    d3.select(ref.current).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 120 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(ref.current)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Y axis (features)
    const y = d3.scaleBand()
      .range([0, height])
      .domain(sortedValues.map(d => d.feature))
      .padding(0.1);
    
    svg.append("g")
      .call(d3.axisLeft(y));

    // X axis (SHAP values)
    const x = d3.scaleLinear()
      .domain(d3.extent(sortedValues, d => d.value))
      .range([0, width]);
      
    svg.append("g")
      .attr("transform", `translate(0, ${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("transform", "translate(-10,0)rotate(-45)")
      .style("text-anchor", "end");

    // Zero line
    svg.append("line")
      .attr("x1", x(0))
      .attr("x2", x(0))
      .attr("y1", 0)
      .attr("y2", height)
      .attr("stroke", "grey")
      .attr("stroke-width", "1.5px")
      .attr("stroke-dasharray", "4");

    // Bars
    svg.selectAll("myRect")
      .data(sortedValues)
      .enter()
      .append("rect")
      .attr("y", d => y(d.feature))
      .attr("height", y.bandwidth())
      .attr("x", d => d.value < 0 ? x(d.value) : x(0))
      .attr("width", d => Math.abs(x(d.value) - x(0)))
      .attr("fill", d => d.value > 0 ? "#e74c3c" : "#3498db"); // Red for positive, Blue for negative

  }, [shapValues]);

  return <svg ref={ref}></svg>;
}

export default ShapBar;