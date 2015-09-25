var gulp = require('gulp');
var gutil = require('gulp-util');

var babel = require('gulp-babel');


gulp.task('build', function () {
    return gulp.src('src/socker.js')
        .pipe(babel({
            modules: 'umd'
        }))
        .pipe(gulp.dest('dist'));
});

gulp.task('default', function () {
    return gulp.start('build');
});
