from tkinter import *
from tkinter import ttk
import tkintermapview
from geopy.geocoders import Nominatim

class MapDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Mappy')
        self.root.geometry("1300x700")
        self.marker_mapping = {}

        # GUI Layout
        self.root.columnconfigure(0, weight=3)  # buttons column
        self.root.columnconfigure(1, weight=1)  # map view column
        self.root.columnconfigure(2, weight=4)  # scroll list column
        self.root.rowconfigure(0, weight=1)

        # Column left
        self.map_frame = Frame(self.root)
        self.map_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.map_widget = tkintermapview.TkinterMapView(self.map_frame, width=800, height=600, corner_radius=0)
        #self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
        #self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
        self.map_widget.set_position(41.620456, -93.601054)  # Initial position
        self.map_widget.set_zoom(16)
        self.map_widget.pack(fill=BOTH, expand=True)

        
        self.map_widget.add_right_click_menu_command(label="Add Marker", command=self.add_marker_event, pass_coords=True)

        # column middle
        self.button_frame = Frame(self.root, padx=1, pady=10)
        self.button_frame.grid(row=0, column=1, sticky="nsew")

        self.add_button = Button(self.button_frame, text="Add Destination", width=20, command=self.add_destination)
        self.add_button.pack(pady=5)

        self.remove_button = Button(self.button_frame, text="Remove Destination", width=20, command=self.remove_destination)
        self.remove_button.pack(pady=5)

        self.edit_button = Button(self.button_frame, text="Edit Destination", width=20, command=self.edit_destination)
        self.edit_button.pack(pady=5)

        # column right
        self.control_frame = Frame(self.root, padx=1, pady=10)
        self.control_frame.grid(row=0, column=2, sticky="nsew")

        self.destinations_label = Label(self.control_frame, text="Destinations")
        self.destinations_label.pack(pady=5)

        self.destinations_listbox = Listbox(self.control_frame, height=25, selectmode=SINGLE)
        self.destinations_listbox.pack(fill=BOTH, expand=True)

        # scrollbar
        self.scrollbar = Scrollbar(self.control_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # lisbox
        self.destinations_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.destinations_listbox.yview)

    
    def get_address(self, coords):
        # using Nominatim to get Address
        geolocator = Nominatim(user_agent="MapPy")
        coordinates = f'{coords[0]},{coords[1]}'
        location = geolocator.reverse((coordinates), exactly_one=True)
        
        if location is None or location.address is None:
            return "Unknown Location"
        
        return location.address

    def add_marker_event(self, coords):
        """Event triggered to add a marker at the clicked coordinates."""
        adr = tkintermapview.convert_coordinates_to_address(coords[0], coords[1])
        

        address = self.get_address(coords)

        print(address)
        
        if address == "Unknown Location":
            address_text = "Unknown Location"
        else:
            name = address.split(',')
            
            address_text = f"{address}"

        # adding address to listbox
        self.destinations_listbox.insert(END, address_text)
        
        # adding marker to map
        new_marker = self.map_widget.set_marker(coords[0], coords[1], text=name[0])
        
        # adding map to list
        self.marker_mapping[address_text] = new_marker



    def add_destination(self):
        """Placeholder for adding a destination manually."""
        print("Add Destination clicked")

    def remove_destination(self):
        """Remove the selected destination from the list and map."""
        selected = self.destinations_listbox.curselection()
        if selected:
            selected_text = self.destinations_listbox.get(selected[0])
            
            # removing item
            self.destinations_listbox.delete(selected[0])
            
            # removing markers
            if selected_text in self.marker_mapping:
                marker = self.marker_mapping.pop(selected_text)
                marker.delete()
            
            print(f"Removed destination: {selected_text}")
        else:
            print("No destination selected")

    def edit_destination(self):
        """Placeholder for editing the selected destination."""
        selected = self.destinations_listbox.curselection()
        if selected:
            print(f"Edit Destination: {self.destinations_listbox.get(selected[0])}")
        else:
            print("No destination selected")



if __name__ == "__main__":
    root = Tk()
    app = MapDisplayApp(root)
    root.mainloop()