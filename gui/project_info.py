import tempfile
import os
import shutil
import webbrowser

def project_info():
    # Absolute path to your logo file - update to your actual path
    logo_source = r"E:\Audio Stenography\enh_project\gui\logo1.jpg"
    logo_filename = os.path.basename(logo_source)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Project Information</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }}
            h1, h2 {{
                color: #333;
            }}
            .header {{
                overflow: auto;
                margin-bottom: 20px;
            }}
            .header img.logo {{
                float: right;
                width: 100px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.13);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: #fff;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="{logo_filename}" alt="Project Logo" class="logo">
            <h1>Project Information</h1>
        </div>
        
        <p>This project was developed by Siva Kumar Reddy, Siva Manikanta Vallepu, 
        T.Venkata Gopi Naveen, T.Nirmala Jyothi, Talluri Ramya, Shaik Tasneem Firdose.  
        This project is designed to secure organizations in the real world 
        from cyber frauds committed by hackers.</p>
        
        <table>
            <thead>
                <tr>
                    <th>Project Details</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Project Name</td><td>Audio Steganography using LSB</td></tr>
                <tr><td>Project Description</td><td>Hiding Message with Encryption in Audio using LSB Algorithm</td></tr>
                <tr><td>Project Start Date</td><td>01-July-2025</td></tr>
                <tr><td>Project End Date</td><td>21-July-2025</td></tr>
                <tr><td>Project Status</td><td><b>Completed</b></td></tr>
            </tbody>
        </table>
        
        <h2>Developer Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Employee ID</th>
                    <th>Email</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Siva Kumar Reddy</td><td>ST#IS#7706</td><td>sivakumarreddy.2204@gmail.com</td></tr>
                <tr><td>Siva Manikanta Vallepu</td><td>ST#IS#7707</td><td>Mkanta86988@gmail.com</td></tr>
                <tr><td>T.Venkata Gopi Naveen</td><td>ST#IS#7709</td><td>naveentulluru@gmail.com</td></tr>
                <tr><td>T.Nirmala Jyothi</td><td>ST#IS#7710</td><td>nimmunirmalajyothi@gmail.com</td></tr>
                <tr><td>Talluri Ramya</td><td>ST#IS#7711</td><td>ramyatalluri445@gmail.com</td></tr>
                <tr><td>Shaik Tasneem Firdose</td><td>ST#IS#7705</td><td>tasneemfirdose264@gmail.com</td></tr>
            </tbody>
        </table>
        
        <h2>Company Information</h2>
        <table>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Name</td><td>Supraja Technologies</td></tr>
                <tr><td>Email</td><td>contact@suprajatechnologies.com</td></tr>
            </tbody>
        </table>
    </body>
    </html>
    """

    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as temp_file:
        temp_file.write(html_code)
        temp_file_path = temp_file.name

    # Copy logo image to the temp directory to be found by HTML
    logo_destination = os.path.join(os.path.dirname(temp_file_path), logo_filename)
    if os.path.exists(logo_source):
        shutil.copy2(logo_source, logo_destination)
    else:
        print(f"Warning: Logo file not found at {logo_source}")

    return temp_file_path  # Return the full path of the generated HTML


def open_project_info():
    """Open the project info in the default web browser."""
    file_path = project_info()
    webbrowser.open('file://' + file_path)
