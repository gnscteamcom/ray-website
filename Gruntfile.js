module.exports = function(grunt) {
	grunt.initConfig({
		pug: {
			dev: {
				options: {
					pretty: true
				},
				files: {
					'index.html': [
						'pug/index.pug',
					]
				}
			}
		},
		compass: {
			dev: {
				options: {
					config: 'config/config.rb'
				}
			}
		},
		watch: {
			pug: {
				files: 'pug/*.pug',
				tasks: ['pug'],
				options: {
					event: ['changed'],
					livereload: true
				},
			},
			scss: {
				files: ['scss/*.scss', 'scss/bootstrap/*.scss'],
				tasks: ['compass'],
				options: {
					event: ['changed'],
					livereload: false
				},
			},
			css: {
				files: 'css/*.css',
				options: {
					event: ['changed'],
					livereload: true
				},
			},
			js: {
				files: 'js/*.js',
				options: {
					event: ['changed'],
					livereload: true
				},
			},
		},
	});

	grunt.loadNpmTasks('grunt-contrib-compass');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-contrib-pug');

	grunt.registerTask('default', ['pug','watch','compass']);
};
