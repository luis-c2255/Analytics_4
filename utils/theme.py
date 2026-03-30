import streamlit as st


class Colors:
    BLUE = "#3A8DFF"
    GREEN = "#4CC9A6"
    RED = "#FF6B6B"
    ORANGE = "#FFB84D"
    CHARCOAL = "#1E1E1E"
    GREY = "#5A6A7A"
    PRUSSIAN = "#0A1A2F"
    PLATINUM = "#F7F9FC"
    DARKGREEN = "#0B2C24"
    LIGHTGREEN = "#247A4D"
    
    
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
        delta_html = f"""
        <p style='color: {delta_color}; margin: 0.5rem 0 0 0; font-size: 1.5rem;'>
            {delta}
        </p>
        """ if delta else ""
        return f"""
        <div style='border: 1px solid {Colors.CHARCOAL};
                    border-top: 4px solid {border_color};
                    padding: 1rem; border-radius: 10px; height: 100%;
                    transition: transform 0.3s ease;'>
            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                <p style='color: {Colors.PLATINUM}; margin: 0; font-size: 0.85rem;
                            text-transform: uppercase; letter-spacing: 1px;'>
                    {title}
                </p>
            </div>
            <p style='color: {Colors.BLUE}; margin: 0; font-size: 1.2rem; font-weight: 700;'>
                    {value}
            </p>
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
    @staticmethod
    def init_page(page_name: str, icon: str = "📊"):
        """Initialize page with common settings"""
        try:
            st.set_page_config(
                page_title=f"{page_name} | Retail Analytics",
                page_icon=icon,
                layout="wide",
            initial_sidebar_state="expanded"
            )
        except:
            # page config already set, skip
            pass
        # Load custom CSS
        try:
            with open ('style.css') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            pass