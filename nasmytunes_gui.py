#!/usr/bin/env python3
"""
NasmyTunes GUI - Desktop Application
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import tempfile
import zipfile
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.simple_bypass import SimpleBypass
from utils.authenticated_bypass import AuthenticatedBypass
from routes.spotify import extract_playlist_id
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class NasmyTunesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NasmyTunes - Spotify to MP3 Converter")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Initialize components
        self.simple_bypass = SimpleBypass()
        self.auth_bypass = AuthenticatedBypass()
        self.setup_spotify()
        self.setup_ui()
        
