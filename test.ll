define i32 @main() {
entry:
    %0 = add i32 %0, 22
    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.deb, i32 0, i32 0), i32 %0)

    ret i32 0
}
@.deb = private unnamed_addr constant [3 x i8] c"%d ", align 4
declare i32 @printf(i8*, ...)
