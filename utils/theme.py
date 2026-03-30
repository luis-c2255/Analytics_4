import streamlit as st

class Colors:
    BLUE = "#3A8DFF"
    GREEN = "#4CC9A6"
    RED = "#FF6B6B"
    ORANGE = "#FFB84D"
    CHARCOAL = "#1E1E1E"
    GREY = "#9EA4A9"
    PRUSSIAN = "#0A1A2F"
    PLATINUM = "#F7F9FC"
    DARKGREEN = "#0B2C24"
    LIGHTGREEN = "#247A4D"
    STEELBLUE = "#5A6A7A"
    
    
class Components:
    @staticmethod
    def metric_card(title: str, value: str, delta: str = "", delta_positive: bool = True, card_type: str = "primary") -> str:
        colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.ORANGE,
        "error": Colors.RED
        }
        border_color = colors.get(card_type, Colors.BLUE)
        delta_color = Colors.GREEN if delta_positive else Colors.RED
        delta_html = (
            f"<p class='metric-delta' style='color:{delta_color};'>{delta}</p>"
            if delta else ""
        )
        return f"""
        <div class='metric-card' style='--bordercolor:{border_color};'>
            <div style='display:flex; align-items:center; margin-bottom:0.5rem;'>
                <p class='metric-title'>{title}</p>
            </div>
            <p class='metric-value'>{value}</p>
            {delta_html}
        </div>
        """
    @staticmethod
    def insight_box(title: str, content: str, box_type: str = "info", min_height: str = "auto") -> str:
        """Create a styled insight/info box with optional min-height"""
        config = {
            "info": {"color": Colors.BLUE, "bg": "rgba(58, 141, 255, 0.15)"},
            "success": {"color": Colors.GREEN, "bg": "rgba(76, 201, 166, 0.15)"},
            "warning": {"color": Colors.ORANGE, "bg": "rgba(255, 184, 77, 0.15)"},
            "error": {"color": Colors.RED, "bg": "rgba(255, 107, 107, 0.15)"}
        }
        style = config.get(box_type, config["info"])
        flex_style = "display: flex; flex-direction: column;" if min_height != "auto" else ""
        height_style = f"min-height: {min_height};" if min_height != "auto" else ""
        return f"""
        <div style='background-color: {style["bg"]};
                    padding: 1rem; border-radius: 8px; margin: 1rem 0;
                    border-left: 6px solid {style["color"]};
                    {height_style} {flex_style}'>
            <h4 style='color: {style["color"]}; margin: 0 0 0.5rem 0;'>{title}</h4>
            <div style='flex-grow: 1; color: {Colors.PLATINUM};'>{content}</div>
        </div>
        """
    @staticmethod
    def page_header(title:str) -> str:
        """Create a styled page header"""
        return f"""
        <div style='background: linear-gradient(135deg, {Colors.DARKGREEN} 0%, {Colors.LIGHTGREEN} 100%);
                    padding: 0.8rem; border-radius: 8px; margin-bottom: 0.8rem;'>
                    <h1 style='color: white; margin: 0; text-align: center; font-size: 2.5rem;'>{title}</h1>
        </div>
        """
