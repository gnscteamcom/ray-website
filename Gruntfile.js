module.exports = function(grunt) {
	grunt.initConfig({
		jade: {
			dev: {
				options: {
					pretty: true
				},
				files: {
					'index.html': [
						'jade/index.jade',
					]
				}
			}
		},
		compass: {
			dev: {
				options: {
					config: 'config.rb'
				}
			}
		},
		watch: {
			jade: {
				files: 'jade/*.jade',
				tasks: ['jade'],
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

	
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-contrib-jade');
	grunt.loadNpmTasks('grunt-contrib-compass');

	grunt.registerTask('default', ['jade','watch','compass']);
};
