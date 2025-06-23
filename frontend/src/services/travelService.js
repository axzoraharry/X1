import api from './api';

export const travelService = {
  // Search flights
  async searchFlights(searchData) {
    try {
      const response = await api.post('/api/travel/flights/search', searchData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to search flights: ${error.message}`);
    }
  },

  // Get flight details
  async getFlight(flightId) {
    try {
      const response = await api.get(`/api/travel/flights/${flightId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get flight details: ${error.message}`);
    }
  },

  // Search hotels
  async searchHotels(searchData) {
    try {
      const response = await api.post('/api/travel/hotels/search', searchData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to search hotels: ${error.message}`);
    }
  },

  // Get hotel details
  async getHotel(hotelId) {
    try {
      const response = await api.get(`/api/travel/hotels/${hotelId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get hotel details: ${error.message}`);
    }
  },

  // Create booking
  async createBooking(bookingData) {
    try {
      const response = await api.post('/api/travel/bookings', bookingData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create booking: ${error.message}`);
    }
  },

  // Get user bookings
  async getUserBookings(userId) {
    try {
      const response = await api.get(`/api/travel/bookings/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get bookings: ${error.message}`);
    }
  },

  // Get booking details
  async getBooking(bookingId) {
    try {
      const response = await api.get(`/api/travel/bookings/detail/${bookingId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get booking details: ${error.message}`);
    }
  },

  // Cancel booking
  async cancelBooking(bookingId) {
    try {
      const response = await api.put(`/api/travel/bookings/${bookingId}/cancel`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to cancel booking: ${error.message}`);
    }
  }
};