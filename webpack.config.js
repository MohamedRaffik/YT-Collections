const path = require('path');
const HTMLWebpackPlugin = require('html-webpack-plugin');
const MiniCSSExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './client/index.js',
    output: {
        path: path.resolve('client/dist'),
        filename: 'main.js'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: 'babel-loader'
            },
            {
                test: /\.scss$/,
                use: [
                    MiniCSSExtractPlugin.loader,
                    'css-loader',
                    'sass-loader',
                    'postcss-loader'
                ]
            },
            {
                test: /\.(png|svg|jpg|gif|ico)$/,
                use: 'file-loader'
            }
        ]
    },
    plugins: [
        new MiniCSSExtractPlugin({
            filename: '[name].css',
            chunkFilename: '[id].css',
        }),
        new HTMLWebpackPlugin({
            template: './client/public/index.html',
            filename: './index.html'
        })
    ],
    devServer: {
        proxy: {
            '/api': {
                target: 'http://localhost:5000',
            }
        },
    }
};