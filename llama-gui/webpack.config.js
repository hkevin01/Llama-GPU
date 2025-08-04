const path = require('path');

module.exports = {
  // Keep the existing webpack configuration from react-scripts
  webpack: {
    configure: (webpackConfig) => {
      // Update the devServer configuration
      if (webpackConfig.devServer) {
        delete webpackConfig.devServer.onBeforeSetupMiddleware;
        delete webpackConfig.devServer.onAfterSetupMiddleware;

        webpackConfig.devServer.setupMiddlewares = (middlewares, devServer) => {
          if (!devServer) {
            throw new Error('webpack-dev-server is not defined');
          }

          // Add your custom middleware here if needed

          return middlewares;
        };
      }

      return webpackConfig;
    }
  }
};
