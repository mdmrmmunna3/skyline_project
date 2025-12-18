const { resolve } = require('path');
const autoprefixer = require('autoprefixer');

const webpack = require('webpack');
const merge = require('webpack-merge');
const HtmlWebPackPlugin = require('html-webpack-plugin');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');

const common = require('./webpack.common');

const { getThemeConfig, getCustomStyleVariables } = require('./utils');

const theme = getThemeConfig();

console.log('theme', theme);

const root = (path) => resolve(__dirname, `../${path}`);

// *** সংশোধিত হোস্ট, পোর্ট, এবং প্রক্সি কনফিগারেশন ***
const host = '0.0.0.0';
const port = 8088;
const proxy = {
  // 1. /api/ রুল (পূর্বের রুল)
  '/api': {
    target: 'http://127.0.0.1:28000',
    changeOrigin: true,
    secure: false,
  },
  // 2. /v3/ এবং /v2.0/ ফিক্স (ড্যাশবোর্ড লোড করার জন্য আবশ্যক)
  '/(v3|v2.0)': {
    target: 'http://127.0.0.1:28000',
    changeOrigin: true,
    secure: false,
  },
};
// *************************************************

module.exports = (env) => {
  const API = (env || {}).API || 'mock';

  console.log('API %s', API);

  const devServer = {
    host,
    port,
    contentBase: root('dist'),
    historyApiFallback: true,
    compress: true,
    hot: true,
    inline: true,
    disableHostCheck: true,
    progress: true,
    stats: {
      children: false,
      chunks: false,
      chunkModules: false,
      modules: false,
      reasons: false,
      useExports: false,
    },
  };

  if (API === 'mock' || API === 'dev') {
    devServer.proxy = proxy;
  }

  const { version, ...restConfig } = common;

  return merge(restConfig, {
    entry: {
      main: root('src/core/index.jsx'),
    },
    output: {
      filename: '[name].js',
      path: root('dist'),
      publicPath: '/',
    },
    mode: 'development',
    devtool: 'cheap-module-eval-source-map',
    devServer,
    module: {
      rules: [
        {
          test: /\.jsx?$/,
          exclude: /node_modules/,
          use: [
            'thread-loader',
            {
              loader: 'babel-loader',
              options: {
                plugins: ['react-refresh/babel'],
              },
            },
          ],
        },
        {
          test: /\.css$/,
          use: [
            {
              loader: 'style-loader',
            },
            'thread-loader',
            {
              loader: 'css-loader',
            },
          ],
        },
        {
          test: /\.(css|less)$/,
          exclude: /node_modules/,
          use: [
            {
              loader: 'style-loader',
            },
            {
              loader: 'css-loader',
              options: {
                modules: {
                  mode: 'global',
                },
                localIdentName: '[name]__[local]--[hash:base64:5]',
              },
            },
            {
              loader: 'postcss-loader',
              options: {
                plugins: [autoprefixer('last 2 version')],
                sourceMap: true,
              },
            },
            {
              loader: 'less-loader',
              options: {
                importLoaders: true,
                javascriptEnabled: true,
              },
            },
            {
              loader: resolve('config/less-replace-loader'),
              options: {
                variableFile: getCustomStyleVariables(),
              },
            },
          ],
        },
        {
          test: /\.(less)$/,
          include: /node_modules/,
          use: [
            {
              loader: 'style-loader',
            },
            'thread-loader',
            {
              loader: 'css-loader',
            },
            {
              loader: 'less-loader',
              options: {
                javascriptEnabled: true,
                modifyVars: theme,
              },
            },
          ],
        },
      ],
    },
    plugins: [
      new ReactRefreshWebpackPlugin({ overlay: false }),
      new webpack.DefinePlugin({
        'process.env.API': JSON.stringify(API),
      }),
      new HtmlWebPackPlugin({
        template: root('src/asset/template/index.html'),
        favicon: root('src/asset/image/favicon.ico'),
      }),
    ],
  });
};