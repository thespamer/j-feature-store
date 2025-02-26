const getApiUrl = () => {
  if (process.env.NODE_ENV === 'production') {
    return process.env.REACT_APP_API_URL || 'http://backend:8000/api/v1';
  }
  return 'http://localhost:8000/api/v1';
};

const config = {
  API_URL: getApiUrl(),
};

export default config;
