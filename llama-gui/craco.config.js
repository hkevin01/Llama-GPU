module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      if (webpackConfig.devServer) {
        delete webpackConfig.devServer.onBeforeSetupMiddleware;
        delete webpackConfig.devServer.onAfterSetupMiddleware;

        webpackConfig.devServer.setupMiddlewares = (middlewares, devServer) => {
          if (!devServer) {
            throw new Error('webpack-dev-server is not defined');
          }
          return middlewares;
        };
      }
      return webpackConfig;
    }
  }
};
