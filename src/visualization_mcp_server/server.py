import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
import networkx as nx
from typing import Any, List, Optional, Union
import json
import io
import base64
from datetime import datetime
from mcp.server.fastmcp import FastMCP, Image

# Initialize FastMCP server
mcp = FastMCP("visualization")

def get_plot_as_image(title: str = "plot") -> Image:
    """Convert the current plot to base64-encoded PNG and return as Image."""
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    # Get bytes data
    image_bytes = buf.read()
    buf.close()
    plt.close()
    
    # Return as Image
    return Image(data=image_bytes, format="png")

@mcp.tool()
async def create_relationship_graph(
    nodes: List[str], 
    edges: List[List[str]], 
    title: str = "Relationship Graph",
    node_size: int = 1000,
    font_size: int = 12
) -> Image:
    """Create a directed relationship graph."""
    try:
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        for edge in edges:
            if len(edge) >= 2:
                G.add_edge(edge[0], edge[1])
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, k=2, iterations=50)
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=node_size, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, arrowstyle='->')
        nx.draw_networkx_labels(G, pos, font_size=font_size, font_weight='bold')
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        return get_plot_as_image("relationship_graph")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating relationship graph: {str(e)}")

@mcp.tool()
async def create_scatter_plot(
    x_data: List[float],
    y_data: List[float],
    labels: Optional[List[str]] = None,
    colors: Optional[List[str]] = None,
    title: str = "Scatter Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    size: int = 50
) -> Image:
    """Create a scatter plot."""
    try:
        plt.figure(figsize=(10, 8))
        if colors is None:
            colors = ['blue'] * len(x_data)
        
        scatter = plt.scatter(x_data, y_data, c=colors, s=size, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        if labels:
            for i, label in enumerate(labels):
                if i < len(x_data) and i < len(y_data):
                    plt.annotate(label, (x_data[i], y_data[i]), 
                                 xytext=(5, 5), textcoords='offset points',
                                 fontsize=10, alpha=0.8)
        
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return get_plot_as_image("scatter_plot")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating scatter plot: {str(e)}")

@mcp.tool()
async def create_3d_plot(
    x_data: List[float],
    y_data: List[float],
    z_data: List[float],
    plot_type: str = "scatter",
    title: str = "3D Plot",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    z_label: str = "Z-axis"
) -> Image:
    """Create a 3D plot (scatter, surface, or wireframe)."""
    try:
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        if plot_type == "scatter":
            ax.scatter(x_data, y_data, z_data, c=z_data, cmap='viridis', s=50)
            
        elif plot_type == "surface":
            x_array = np.array(x_data)
            y_array = np.array(y_data)
            z_array = np.array(z_data)
            unique_x = sorted(set(x_data))
            unique_y = sorted(set(y_data))
            
            if len(unique_x) * len(unique_y) == len(z_data):
                X = np.array(unique_x)
                Y = np.array(unique_y)
                X, Y = np.meshgrid(X, Y)
                Z = np.array(z_data).reshape(len(unique_y), len(unique_x))
                ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            else:
                ax.scatter(x_data, y_data, z_data, c=z_data, cmap='viridis', s=50)
                
        elif plot_type == "wireframe":
            unique_x = sorted(set(x_data))
            unique_y = sorted(set(y_data))
            if len(unique_x) * len(unique_y) == len(z_data):
                X = np.array(unique_x)
                Y = np.array(unique_y)
                X, Y = np.meshgrid(X, Y)
                Z = np.array(z_data).reshape(len(unique_y), len(unique_x))
                ax.plot_wireframe(X, Y, Z, alpha=0.8)
            else:
                ax.scatter(x_data, y_data, z_data, c=z_data, cmap='viridis', s=50)
        
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_zlabel(z_label)
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        return get_plot_as_image("3d_plot")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating 3D plot: {str(e)}")

@mcp.tool()
async def create_classification_plot(
    x_data: List[float],
    y_data: List[float],
    categories: List[str],
    title: str = "Classification Scatter Plot",
    x_label: str = "Feature 1",
    y_label: str = "Feature 2"
) -> Image:
    """Create a scatter plot with classification categories."""
    try:
        plt.figure(figsize=(10, 8))
        unique_categories = list(set(categories))
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_categories)))
        
        for i, category in enumerate(unique_categories):
            mask = [cat == category for cat in categories]
            x_cat = [x for x, m in zip(x_data, mask) if m]
            y_cat = [y for y, m in zip(y_data, mask) if m]
            plt.scatter(x_cat, y_cat, c=[colors[i]], label=category, 
                        s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
        
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return get_plot_as_image("classification_plot")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating classification plot: {str(e)}")

@mcp.tool()
async def create_histogram(
    data: List[float],
    bins: int = 30,
    title: str = "Histogram",
    x_label: str = "Value",
    y_label: str = "Frequency"
) -> Image:
    """Create a histogram."""
    try:
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=bins, alpha=0.7, color='skyblue', edgecolor='black', linewidth=0.5)
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        return get_plot_as_image("histogram")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating histogram: {str(e)}")

@mcp.tool()
async def create_line_plot(
    x_data: List[float],
    y_data: List[float],
    title: str = "Line Chart",
    x_label: str = "X-axis",
    y_label: str = "Y-axis",
    line_style: str = "-",
    color: str = "blue"
) -> Image:
    """Create a line chart."""
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(x_data, y_data, linestyle=line_style, color=color, linewidth=2, marker='o', markersize=4)
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return get_plot_as_image("line_plot")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating line chart: {str(e)}")

@mcp.tool()
async def create_heatmap(
    data: List[List[float]],
    x_labels: Optional[List[str]] = None,
    y_labels: Optional[List[str]] = None,
    title: str = "Heatmap",
    colormap: str = "viridis"
) -> Image:
    """Create a heatmap from 2D data."""
    try:
        plt.figure(figsize=(10, 8))
        im = plt.imshow(data, cmap=colormap, aspect='auto')
        
        if x_labels:
            plt.xticks(range(len(x_labels)), x_labels, rotation=45, ha='right')
        if y_labels:
            plt.yticks(range(len(y_labels)), y_labels)
        
        plt.colorbar(im, shrink=0.8)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return get_plot_as_image("heatmap")
        
    except Exception as e:
        plt.close()
        raise Exception(f"Error creating heatmap: {str(e)}")

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
