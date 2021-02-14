# imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pygame import mixer
import pygame
import os
import time
import threading
from ttkthemes import themed_tk as themes

mixer.init()  # initialize the mixer


class Player:
    def __init__(self, master):
        """All the variables are created here to make them globally accessible"""
        self.master = master
        self.spacing = "                                                   "
        self.title = "MIA Player"
        self.master.title(self.title)
        self.icon = "./images/icon.ico"
        self.master.iconbitmap(self.icon)
        self.master.geometry("800x500")
        self.master.resizable(False, False)
        self.isMute = False
        self.isPlaying = None
        self.isPaused = None
        self.endOfFile = False
        self.currentVolume = 0.4
        self.file = None
        self.playList = []
        self.currentFileIndex = None
        self.currentFile = None
        self.isTracksLoaded = False

        # menu bar
        self.menuBar = tk.Menu(self.master)
        self.master.configure(menu=self.menuBar)

        # the file menu option
        self.submenu = tk.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='File', menu=self.submenu)
        self.submenu.add_command(label='Open File', command=self.open_file)
        self.submenu.add_command(label='Open Folder', command=self.open_folder)
        self.submenu.add_command(label='Exit', command=self.exit)

        # the about menu option
        self.submenu = tk.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Help', menu=self.submenu)
        self.submenu.add_command(label='About', command=self.about_app)

        # ui elements
        # styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="green")

        # images
        # player images
        self.playImage = tk.PhotoImage(file="./images/play.gif")
        self.pauseImage = tk.PhotoImage(file="./images/pause.gif")
        self.stopImage = tk.PhotoImage(file="./images/stop.gif")
        self.nextImage = tk.PhotoImage(file="./images/next_track.gif")
        self.prevImage = tk.PhotoImage(file="./images/previous_track.gif")
        self.rewindImage = tk.PhotoImage(file="./images/rewind.gif")

        # file and folder images
        self.openFileImage = tk.PhotoImage(file="./images/add_file.gif")
        self.openFolderImage = tk.PhotoImage(file="./images/add_directory.gif")
        self.deleteFileImage = tk.PhotoImage(file="./images/delete_selected.gif")
        self.clearPlayListImage = tk.PhotoImage(file="./images/clear_play_list.gif")

        # volume images
        self.volumeImage = tk.PhotoImage(file="./images/unmute.gif")
        self.muteImage = tk.PhotoImage(file="./images/mute.gif")

        # frames
        self.style.configure("Frame1.TFrame", background="black")
        self.bottomContainer = tk.ttk.Frame(self.master, height=100, width=800, style="Frame1.TFrame")
        self.style.configure("Frame2.TFrame", background="gray44")
        self.listContainer = tk.ttk.Frame(self.master, height=330, width=800, style="Frame2.TFrame")
        self.style.configure("Frame3.TFrame", background="gray44")
        self.playListControls = tk.ttk.Frame(self.master, width=800, height=50, style="Frame3.TFrame", relief=tk.GROOVE)

        # items
        # play
        self.playButton = tk.ttk.Button(self.bottomContainer, image=self.playImage, command=self.toggle_play_pause)
        self.playButton.image = self.playImage

        # stop
        self.stopButton = tk.ttk.Button(self.bottomContainer, image=self.stopImage, command=self.stop_track)
        self.stopButton.image = self.stopImage

        # next
        self.nextButton = tk.ttk.Button(self.bottomContainer, image=self.nextImage, command=self.play_next_track)
        self.nextButton.image = self.nextImage

        # previous button
        self.previousButton = tk.ttk.Button(self.bottomContainer, image=self.prevImage,
                                            command=self.play_previous_track)
        self.previousButton.image = self.prevImage

        # rewind (repeat)
        self.rewindButton = tk.ttk.Button(self.bottomContainer, image=self.rewindImage, command=self.rewind_track)
        self.rewindButton.image = self.rewindImage

        # open file
        self.openFile = tk.ttk.Button(self.playListControls, image=self.openFileImage, command=self.open_file)
        self.openFile.image = self.openFileImage

        # delete file
        self.deleteFile = tk.ttk.Button(self.playListControls, image=self.deleteFileImage,
                                        command=self.delete_selected_file)
        self.deleteFile.image = self.openFileImage

        # open folder
        self.openFolderButton = tk.ttk.Button(self.playListControls, image=self.openFolderImage,
                                              command=self.open_folder)
        self.openFolderButton.image = self.openFolderImage

        # clear play list
        self.clearPlayList = tk.ttk.Button(self.playListControls, image=self.clearPlayListImage,
                                           command=self.clear_playlist)
        self.clearPlayList.image = self.clearPlayListImage

        # volume bar
        self.volumeBar = tk.ttk.Scale(self.bottomContainer, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_vol)
        self.volumeBar.set(40)
        mixer.music.set_volume(0.4)
        # volume button
        self.volumeButton = tk.ttk.Button(self.bottomContainer, image=self.volumeImage, command=self.toggle_mute)
        self.volumeButton.image = self.volumeImage

        # list the tracks
        self.tracksBox = tk.Listbox(self.listContainer, width=800, height=400, bg="grey33", fg="white")

        # track length label
        self.style.configure("Label1.TLabel", background="black", foreground="white")
        self.durationLabel = tk.ttk.Label(self.bottomContainer, text="", style="Label1.TLabel")

        # current playing file label
        self.style.configure("Label2.TLabel", background="black", foreground="white")
        self.playingFileLabel = tk.ttk.Label(self.bottomContainer, text="", style="Label2.TLabel")

        # status bar
        self.statusBar = tk.Label(self.master, text="Welcome to MiaPlayer...", bd=2, relief=tk.SUNKEN,
                                  anchor=tk.W, bg="black", fg="white", padx=20)

        # main iu placements
        self.ui()

    # ui
    def ui(self):
        """This is the entire ui design"""
        # frames
        self.bottomContainer.place(x=0, y=380)
        self.listContainer.place(x=0, y=0)
        self.playListControls.place(x=0, y=330)

        # play list controls
        self.clearPlayList.place(x=300, y=6)
        self.openFolderButton.place(x=350, y=6)
        self.openFile.place(x=400, y=6)
        self.deleteFile.place(x=450, y=6)

        # play controls
        self.rewindButton.place(x=250, y=55)
        self.previousButton.place(x=300, y=55)
        self.playButton.place(x=350, y=55)
        self.nextButton.place(x=400, y=55)
        self.stopButton.place(x=450, y=55)

        self.tracksBox.place(x=0, y=0)

        # volume
        self.volumeBar.place(x=690, y=63)
        self.volumeButton.place(x=640, y=53)

        # playing file label
        self.playingFileLabel.place(x=100, y=20, bordermode=tk.OUTSIDE)
        self.durationLabel.place(x=600, y=20, bordermode=tk.OUTSIDE)

        # status bar
        self.statusBar.place(x=0, y=480, width=800, bordermode=tk.INSIDE)

    # open a file to add its content to the playlist
    def open_file(self):
        """open a single file and add it to the play list"""
        self.file = filedialog.askopenfilename(filetypes=(("Audio Files", ".mp3 .wav .ogg"), ("All Files", "*.*")))
        self.tracksBox.insert("end", os.path.basename(self.file))
        self.playList.append(self.file)
        self.isTracksLoaded = True

    # open a folder and add its content to the listbox
    def open_folder(self):
        """Open and add all the media files in a folder to the play list"""
        directory_path = tk.filedialog.askdirectory()
        audio_files_in_directory = []
        if not directory_path:
            return
        for (dir_path, dir_names, filenames) in os.walk(directory_path):
            for audio_file in filenames:
                if audio_file.endswith(".mp3") or audio_file.endswith(".wav"):
                    audio_files_in_directory.append(f"{dir_path}/{audio_file}")
        for track in audio_files_in_directory:
            self.playList.append(track)
            self.tracksBox.insert("end", os.path.basename(track))
        self.isTracksLoaded = True

    def delete_selected_file(self):
        """Delete the currently selected file from the playlist"""
        if self.currentFileIndex is not None:
            self.playList.pop(self.currentFileIndex)
            self.tracksBox.delete(self.currentFileIndex)
        else:
            selected_file = self.tracksBox.curselection()
            selected_file = int(selected_file[0])
            self.playList.pop(selected_file)
            self.tracksBox.delete(selected_file)

    def clear_playlist(self):
        """Clear the current playlist"""
        self.playList.clear()
        self.tracksBox.delete(0, "end")

    # show the details of the playing file
    def show_details(self, track):
        """Show the details of the current playing file"""
        self.playingFileLabel["text"] = f"{os.path.basename(track)}"
        playing_file = mixer.Sound(track)
        duration = playing_file.get_length()
        # split into minutes and seconds
        minutes, seconds = divmod(duration, 60)
        minutes = round(minutes)
        seconds = round(seconds)
        time_format = "{:02d} : {:02d}".format(minutes, seconds)
        self.durationLabel["text"] = time_format

        t1 = threading.Thread(target=self.start_count, args=(duration,))
        t1.start()

    def start_count(self, t):
        """Start the count for the duration of the currently playing file"""
        self.endOfFile = False
        while t and mixer.music.get_busy():
            if self.isPaused:
                continue
            else:
                minutes, seconds = divmod(t, 60)
                minutes = round(minutes)
                seconds = round(seconds)
                time_format = "{:02d} : {:02d}".format(minutes, seconds)
                self.durationLabel['text'] = "" + time_format
                time.sleep(1)
                t -= 1
        self.endOfFile = True
        if self.endOfFile:
            self.play_next_track()

    # toggle play and pause of the current track
    def toggle_play_pause(self):
        """Toggle the pause and play functionality of the player"""
        try:
            if self.file is None and not self.isTracksLoaded:
                self.file = filedialog.askopenfilename(
                    filetypes=(("Audio Files", ".mp3 .wav"), ("All Files", "*.*")))
                self.tracksBox.insert("end", os.path.basename(self.file))
                mixer.music.load(self.file)
                mixer.music.play()
                self.isPlaying = True
                self.isPaused = False
                self.statusBar["text"] = f"Playing - {os.path.basename(self.file)}"
                self.playButton['image'] = self.pauseImage
                self.playButton.image = self.pauseImage
                self.show_details(self.file)
                self.master.title(f"{self.title} {self.spacing} {os.path.basename(self.file)}")
            else:
                if self.isPlaying is None:
                    try:
                        self.currentFile = self.tracksBox.curselection()
                        self.currentFile = self.currentFile[0]
                        self.currentFileIndex = int(self.currentFile)
                        self.currentFile = self.playList[self.currentFile]
                        mixer.music.load(self.currentFile)
                        mixer.music.play()
                        self.playButton['image'] = self.pauseImage
                        self.playButton.image = self.pauseImage
                        self.show_details(self.currentFile)
                        self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
                        self.master.title(f"{self.title} {self.spacing} {os.path.basename(self.currentFile)}")
                        self.isPlaying = True
                        self.isPaused = False
                        self.isTracksLoaded = True
                    except IndexError:
                        self.currentFile = self.playList[0]
                        self.currentFileIndex = 0
                        self.isPlaying = True
                        self.isPaused = False
                        self.isTracksLoaded = True
                        mixer.music.load(self.currentFile)
                        mixer.music.play()
                        self.playButton['image'] = self.pauseImage
                        self.playButton.image = self.pauseImage
                        self.show_details(self.currentFile)
                        self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
                elif self.isPlaying:
                    mixer.music.pause()
                    self.isPlaying = False
                    self.isPaused = True
                    self.playButton['image'] = self.playImage
                    self.playButton.image = self.playImage
                    self.show_details(self.currentFile)
                    self.statusBar["text"] = f"paused"
                elif self.isPaused:
                    mixer.music.unpause()
                    self.isPlaying = True
                    self.isPaused = False
                    self.playButton['image'] = self.pauseImage
                    self.playButton.image = self.pauseImage
                    self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
        except TypeError:
            pass

    # play next track
    def play_next_track(self):
        """Play the next track on the playlist if any"""
        try:
            if self.currentFile is not None:
                self.currentFileIndex += 1
                mixer.music.stop()
                time.sleep(1)
                self.currentFile = self.playList[self.currentFileIndex]
                mixer.music.load(self.currentFile)
                mixer.music.play()
                self.show_details(self.currentFile)
                self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
                self.master.title(f"{self.title} {self.spacing} {os.path.basename(self.currentFile)}")
                self.isPlaying = True
                self.isPaused = False
            else:
                pass
        except IndexError:
            self.rewind_track()

    def play_previous_track(self):
        """Play the previous track on the playlist if any"""
        try:
            if self.currentFile is not None:
                self.currentFileIndex -= 1
                self.currentFile = self.playList[self.currentFileIndex]
                mixer.music.stop()
                time.sleep(1)
                mixer.music.load(self.currentFile)
                mixer.music.play()
                self.show_details(self.currentFile)
                self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
                self.master.title(f"{self.title} {self.spacing} {os.path.basename(self.currentFile)}")
                self.isPlaying = True
                self.isPaused = False
            else:
                pass
        except IndexError:
            self.rewind_track()

    # rewind the current playing track
    def rewind_track(self):
        """start the currently playing track again (rewind the track)"""
        try:
            if self.currentFile is None:
                pass
            else:
                if self.isPlaying:
                    mixer.music.stop()
                    self.isPaused = False
                    self.isPlaying = True
                    mixer.music.load(self.currentFile)
                    mixer.music.play()
                    self.show_details(self.currentFile)
                    self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
                    self.master.title(f"{self.title} {self.spacing} {os.path.basename(self.currentFile)}")
                    self.playButton['image'] = self.pauseImage
                    self.playButton.image = self.pauseImage
                else:
                    self.isPaused = False
                    self.isPlaying = True
                    mixer.music.stop()
                    mixer.music.load(self.currentFile)
                    mixer.music.play()
                    self.show_details(self.currentFile)
                    self.statusBar["text"] = f"Playing - {os.path.basename(self.currentFile)}"
                    self.playButton['image'] = self.pauseImage
                    self.playButton.image = self.pauseImage
        except TypeError:
            self.statusBar["text"] = "No file is paying"

    def stop_track(self):
        """This method stops the current playing truck"""
        try:
            if self.currentFile is None:
                pass
            else:
                self.isPlaying = None
                self.isPaused = None
                self.currentFile = None
                self.playButton['image'] = self.playImage
                self.playButton.image = self.playImage
                mixer.music.stop()
                self.master.title(f"{self.title}")
                self.statusBar["text"] = "Welcome to MiaPlayer..."
                self.playingFileLabel["text"] = ""
                self.durationLabel["text"] = ""
        except pygame.error:
            print("No file Playing")

    # set the volume function
    def set_vol(self, val):
        """This method changes the volume of the music player"""
        if self.isMute:
            volume = float(val) / 100
            mixer.music.set_volume(volume)
            self.volumeButton['image'] = self.volumeImage
            self.isMute = False
        else:
            volume = float(val) / 100
            mixer.music.set_volume(volume)
            self.isMute = False

    # toggle mute and un-mute function
    def toggle_mute(self):
        """This method toggles the mute and unmute function of the player"""
        if self.isMute:
            mixer.music.set_volume(self.currentVolume)
            self.volumeBar.set(self.currentVolume * 100)
            self.volumeButton['image'] = self.volumeImage
            self.volumeButton.image = self.volumeImage
            self.isMute = False
        else:
            mixer.music.set_volume(0)
            self.volumeBar.set(0)
            self.volumeButton['image'] = self.muteImage
            self.volumeButton.image = self.muteImage
            self.isMute = True

    def about_app(self):
        """Tell the user about this application"""
        about_title = f"About {self.title}"
        about_message = f"{self.title}, is created with pure python by Musah Ibrahim Ali"
        messagebox.showinfo(about_title, about_message)

    def exit(self):
        """Exit the app"""
        self.stop_track()
        self.master.destroy()


# main function that creates the app
def main():
    """The root or main engine of the app"""
    root = themes.ThemedTk()
    root.get_themes()  # Returns a list of all themes that can be set
    root.set_theme("kroc")  # ubuntu, winxpblue, radiance, kroc^^, elegance, clearlooks, blue, arc^^
    Player(root)
    # root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
