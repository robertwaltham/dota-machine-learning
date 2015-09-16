var browserify = require('browserify');
var gulp = require('gulp');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var gutil = require('gulp-util');
var uglify = require('gulp-uglify');
var sourcemaps = require('gulp-sourcemaps');
var reactify = require('reactify');

var script_path = './js/*.jsx';

gulp.task('dev', function () {
    // set up the browserify instance on a task basis
    var b = browserify({
        entries: './js/stats-ui.jsx',
        debug: true,
        // defining transforms here will avoid crashing your stream
        transform: [reactify]
    });

    return b.bundle()
        .pipe(source('stats-ui.jsx'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        //.pipe(uglify())
        .on('error', gutil.log)
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('./static/js/'));
});

gulp.task('prod', function () {
    // set up the browserify instance on a task basis
    var b = browserify({
        entries: './js/stats-ui.jsx',
        debug: true,
        // defining transforms here will avoid crashing your stream
        transform: [reactify]
    });

    return b.bundle()
        .pipe(source('stats-ui.jsx'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .pipe(uglify())
        .on('error', gutil.log)
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('./static/js/'));
});


// Rerun the task when a file changes
gulp.task('watch', function() {
  gulp.watch(script_path, ['dev']);
});