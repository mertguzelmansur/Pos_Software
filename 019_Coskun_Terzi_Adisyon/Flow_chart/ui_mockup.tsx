import React, { useState, useEffect } from "react";

// Main application component
export default function TailorShopSystem() {
  // State variables
  const [customers, setCustomers] = useState([
    { id: 1, name: "John", surname: "Doe", phone: "555-1234", location: "Downtown" },
    { id: 2, name: "Jane", surname: "Smith", phone: "555-5678", location: "Uptown" },
    { id: 3, name: "Alex", surname: "Johnson", phone: "555-9012", location: "Westside" }
  ]);
  
  const [services] = useState([
    { id: 1, name: "Hem Pants", price: 12 },
    { id: 2, name: "Replace Zipper", price: 15 },
    { id: 3, name: "Patch Repair", price: 8 },
    { id: 4, name: "Button Replacement", price: 5 },
    { id: 5, name: "Resize Garment", price: 25 }
  ]);
  
  // UI state
  const [view, setView] = useState("customerSelect"); // customerSelect, newCustomer, serviceSelect, preview
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [customerNote, setCustomerNote] = useState("");
  const [newCustomer, setNewCustomer] = useState({
    name: "",
    surname: "",
    phone: "",
    location: ""
  });

  // Filtered customers based on search
  const filteredCustomers = customers.filter(customer => 
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.surname.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm)
  );

  // Calculate total price
  const totalPrice = selectedService ? selectedService.price * quantity : 0;
  
  // Current date for the label
  const currentDate = new Date().toLocaleDateString();

  // Handle customer selection
  const selectCustomer = (customer) => {
    setSelectedCustomer(customer);
    setView("serviceSelect");
  };

  // Handle service selection
  const selectService = (service) => {
    setSelectedService(service);
  };

  // Save new customer
  const saveNewCustomer = () => {
    const customer = {
      id: customers.length + 1,
      ...newCustomer
    };
    setCustomers([...customers, customer]);
    setSelectedCustomer(customer);
    setView("serviceSelect");
  };

  // Proceed to preview
  const proceedToPreview = () => {
    setView("preview");
  };

  // Print label (mock function)
  const printLabel = () => {
    alert("Label sent to printer!");
    resetForm();
  };

  // Reset form
  const resetForm = () => {
    setView("customerSelect");
    setSearchTerm("");
    setSelectedCustomer(null);
    setSelectedService(null);
    setQuantity(1);
    setCustomerNote("");
    setNewCustomer({
      name: "",
      surname: "",
      phone: "",
      location: ""
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">Tailor Shop Management System</h1>
      </header>
      
      <main className="flex-grow p-4">
        {/* Customer Selection View */}
        {view === "customerSelect" && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Select Customer</h2>
            
            <div className="mb-4">
              <input
                type="text"
                placeholder="Search by name or phone..."
                className="w-full p-2 border rounded"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="mb-4 max-h-64 overflow-y-auto">
              {filteredCustomers.length > 0 ? (
                <ul className="divide-y">
                  {filteredCustomers.map(customer => (
                    <li 
                      key={customer.id}
                      className="p-2 hover:bg-blue-50 cursor-pointer"
                      onClick={() => selectCustomer(customer)}
                    >
                      <div className="font-medium">{customer.name} {customer.surname}</div>
                      <div className="text-sm text-gray-600">{customer.phone}</div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-gray-500">No customers found</div>
              )}
            </div>
            
            <button 
              className="bg-green-500 text-white px-4 py-2 rounded"
              onClick={() => setView("newCustomer")}
            >
              New Customer
            </button>
          </div>
        )}
        
        {/* New Customer Registration View */}
        {view === "newCustomer" && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">New Customer</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded mt-1"
                  value={newCustomer.name}
                  onChange={(e) => setNewCustomer({...newCustomer, name: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Surname</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded mt-1"
                  value={newCustomer.surname}
                  onChange={(e) => setNewCustomer({...newCustomer, surname: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Phone Number</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded mt-1"
                  value={newCustomer.phone}
                  onChange={(e) => setNewCustomer({...newCustomer, phone: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Location</label>
                <input
                  type="text"
                  className="w-full p-2 border rounded mt-1"
                  value={newCustomer.location}
                  onChange={(e) => setNewCustomer({...newCustomer, location: e.target.value})}
                />
              </div>
            </div>
            
            <div className="mt-6 flex space-x-4">
              <button 
                className="bg-gray-300 px-4 py-2 rounded"
                onClick={() => setView("customerSelect")}
              >
                Cancel
              </button>
              <button 
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={saveNewCustomer}
              >
                Save Customer
              </button>
            </div>
          </div>
        )}
        
        {/* Service Selection View */}
        {view === "serviceSelect" && selectedCustomer && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-2">Select Service</h2>
            <p className="mb-4 text-blue-600">
              Customer: {selectedCustomer.name} {selectedCustomer.surname}
            </p>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Repair Type</label>
              <select 
                className="w-full p-2 border rounded"
                onChange={(e) => selectService(services.find(s => s.id === parseInt(e.target.value)))}
                value={selectedService?.id || ""}
              >
                <option value="">Select a service...</option>
                {services.map(service => (
                  <option key={service.id} value={service.id}>
                    {service.name} - ${service.price}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
              <input
                type="number"
                min="1"
                className="w-full p-2 border rounded"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Customer Notes</label>
              <textarea
                className="w-full p-2 border rounded"
                rows="3"
                value={customerNote}
                onChange={(e) => setCustomerNote(e.target.value)}
              ></textarea>
            </div>
            
            {selectedService && (
              <div className="mb-4 p-3 bg-blue-50 rounded">
                <p className="font-medium">Total Price: ${totalPrice.toFixed(2)}</p>
              </div>
            )}
            
            <div className="flex space-x-4">
              <button 
                className="bg-gray-300 px-4 py-2 rounded"
                onClick={() => setView("customerSelect")}
              >
                Back
              </button>
              <button 
                className="bg-blue-500 text-white px-4 py-2 rounded"
                onClick={proceedToPreview}
                disabled={!selectedService}
              >
                Continue
              </button>
            </div>
          </div>
        )}
        
        {/* Preview View */}
        {view === "preview" && selectedCustomer && selectedService && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Preview Label</h2>
            
            <div className="mb-6 border-2 border-dashed border-gray-300 p-4 bg-gray-50">
              <div className="text-center mb-2 font-bold border-b pb-1">TAILOR SHOP</div>
              
              <div className="grid grid-cols-2 gap-1 text-sm">
                <div className="font-medium">Customer:</div>
                <div>{selectedCustomer.name} {selectedCustomer.surname}</div>
                
                <div className="font-medium">Phone:</div>
                <div>{selectedCustomer.phone}</div>
                
                <div className="font-medium">Service:</div>
                <div>{selectedService.name}</div>
                
                <div className="font-medium">Quantity:</div>
                <div>{quantity}</div>
                
                <div className="font-medium">Total Price:</div>
                <div>${totalPrice.toFixed(2)}</div>
                
                <div className="font-medium">Date:</div>
                <div>{currentDate}</div>
              </div>
              
              {customerNote && (
                <div className="mt-2 pt-1 border-t text-sm">
                  <div className="font-medium">Notes:</div>
                  <div>{customerNote}</div>
                </div>
              )}
            </div>
            
            <div className="flex space-x-4">
              <button 
                className="bg-gray-300 px-4 py-2 rounded"
                onClick={() => setView("serviceSelect")}
              >
                Back
              </button>
              <button 
                className="bg-green-500 text-white px-4 py-2 rounded"
                onClick={printLabel}
              >
                Print Label
              </button>
            </div>
          </div>
        )}
      </main>
      
      <footer className="bg-gray-200 p-4 text-center text-gray-600">
        Tailor Shop Management System
      </footer>
    </div>
  );
}