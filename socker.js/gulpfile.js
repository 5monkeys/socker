var gulp = require('gulp');
var gutil = require('gulp-util');

var es6transpiler = require('gulp-es6-transpiler');

gulp.task('build', function () {
    return gulp.src('src/socker.js')
        .pipe(es6transpiler())
        .pipe(gulp.dest('dist'));
});

gulp.task('default', function () {
    return gulp.start('build');
});