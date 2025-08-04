const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      changeOrigin: true,
      ws: true,
      onProxyReq: function(proxyReq) {
        // Log proxy requests in development
        if (process.env.NODE_ENV === 'development') {
          console.log('Proxying:', proxyReq.path);
        }
      },
    })
  );
};
